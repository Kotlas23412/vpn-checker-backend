import os
import re
import socket
import ssl
import time
import json
import requests
import base64
import websocket
import shutil
import threading
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# ------------------ Настройки ------------------
BASE_DIR = "checked"
FOLDER_RU = os.path.join(BASE_DIR, "RU_Best")
FOLDER_EURO = os.path.join(BASE_DIR, "My_Euro")

if os.path.exists(FOLDER_RU):
    shutil.rmtree(FOLDER_RU)
if os.path.exists(FOLDER_EURO):
    shutil.rmtree(FOLDER_EURO)
os.makedirs(FOLDER_RU, exist_ok=True)
os.makedirs(FOLDER_EURO, exist_ok=True)

TIMEOUT = 5
socket.setdefaulttimeout(TIMEOUT)
THREADS = 40

CACHE_HOURS = 6
CHUNK_LIMIT = 1000
EURO_CHUNK_LIMIT = 500
MAX_KEYS_TO_CHECK = 10**9      # было 30000

MAX_PING_MS = 3000
FAST_LIMIT = 10**9             # было 3000
MAX_HISTORY_AGE = 2 * 24 * 3600

# Дисковый кэш IP → страна
IP_CACHE_FILE = os.path.join(BASE_DIR, "ip_cache.json")
IP_CACHE_MAX_AGE_DAYS = 30

# ip-api: не более ~40 req/min — берём 38 для запаса
GEO_API_RATE_LIMIT = 38
GEO_API_WINDOW = 60.0

RU_FILES = ["ru_white_part1.txt", "ru_white_part2.txt", "ru_white_part3.txt", "ru_white_part4.txt"]
EURO_FILES = ["my_euro_part1.txt", "my_euro_part2.txt", "my_euro_part3.txt"]

HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
MY_CHANNEL = "@vlesstrojan"

URLS_RU = [
    "https://github.com/igareck/vpn-configs-for-russia/blob/main/BLACK_VLESS_RUS_mobile.txt",
    "https://github.com/igareck/vpn-configs-for-russia/blob/main/BLACK_SS%2BAll_RUS.txt",
    "https://github.com/igareck/vpn-configs-for-russia/blob/main/Vless-Reality-White-Lists-Rus-Mobile-2.txt",
    "https://github.com/igareck/vpn-configs-for-russia/blob/main/Vless-Reality-White-Lists-Rus-Mobile.txt",
    "https://github.com/igareck/vpn-configs-for-russia/blob/main/WHITE-CIDR-RU-all.txt",
    "https://github.com/igareck/vpn-configs-for-russia/blob/main/WHITE-CIDR-RU-checked.txt",
    "https://github.com/igareck/vpn-configs-for-russia/blob/main/WHITE-SNI-RU-all.txt",
    "https://raw.githubusercontent.com/zieng2/wl/main/vless.txt",
    "https://raw.githubusercontent.com/LowiKLive/BypassWhitelistRu/refs/heads/main/WhiteList-Bypass_Ru.txt",
    "https://raw.githubusercontent.com/zieng2/wl/main/vless_universal.txt",
    "https://raw.githubusercontent.com/vsevjik/OBSpiskov/refs/heads/main/wwh",
    "https://jsnegsukavsos.hb.ru-msk.vkcloud-storage.ru/love",
    "https://etoneya.a9fm.site/1",
    "https://s3c3.001.gpucloud.ru/vahe4xkwi/cjdr"
]

URLS_MY = [
    "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/refs/heads/main/githubmirror/new/all_new.txt",
    "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/refs/heads/main/githubmirror/clean/vless.txt",
    "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/refs/heads/main/githubmirror/clean/vmess.txt",
    "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/refs/heads/main/githubmirror/clean/trojan.txt",
    "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/refs/heads/main/githubmirror/clean/ss.txt",
    "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/refs/heads/main/githubmirror/clean/hysteria.txt",
    "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/refs/heads/main/githubmirror/clean/hysteria2.txt",
    "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/refs/heads/main/githubmirror/clean/hy2.txt",
    "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/refs/heads/main/githubmirror/clean/tuic.txt",
]

EURO_CODES = {
    "NL", "DE", "FI", "GB", "FR", "SE", "PL", "CZ", "AT", "CH",
    "IT", "ES", "NO", "DK", "BE", "IE", "LU", "EE", "LV", "LT"
}
BAD_MARKERS = ["CN", "IR", "KR", "BR", "IN", "RELAY", "POOL", "🇨🇳", "🇮🇷", "🇰🇷"]

RU_MARKERS_STRICT = [
    ".ru", "moscow", "msk", "spb", "saint-peter", "russia",
    "россия", "москва", "питер", "ru-", "-ru.",
    "178.154.", "77.88.", "5.255.", "87.250.",
    "95.108.", "213.180.", "195.208.",
    "91.108.", "149.154.",
]

COUNTRY_NAMES_RU = {
    "RU": "Россия", "NL": "Нидерланды", "DE": "Германия", "FI": "Финляндия",
    "GB": "Великобритания", "FR": "Франция", "SE": "Швеция", "PL": "Польша",
    "CZ": "Чехия", "AT": "Австрия", "CH": "Швейцария", "IT": "Италия",
    "ES": "Испания", "NO": "Норвегия", "DK": "Дания", "BE": "Бельгия",
    "IE": "Ирландия", "LU": "Люксембург", "EE": "Эстония", "LV": "Латвия",
    "LT": "Литва",
}

COUNTRY_FLAGS = {
    "RU": "🇷🇺", "NL": "🇳🇱", "DE": "🇩🇪", "FI": "🇫🇮", "GB": "🇬🇧",
    "FR": "🇫🇷", "SE": "🇸🇪", "PL": "🇵🇱", "CZ": "🇨🇿", "AT": "🇦🇹",
    "CH": "🇨🇭", "IT": "🇮🇹", "ES": "🇪🇸", "NO": "🇳🇴", "DK": "🇩🇰",
    "BE": "🇧🇪", "IE": "🇮🇪", "LU": "🇱🇺", "EE": "🇪🇪", "LV": "🇱🇻",
    "LT": "🇱🇹",
}

def country_to_title_ru(code: str) -> str:
    return COUNTRY_NAMES_RU.get(code, code or "UNKNOWN")

def country_to_flag(code: str) -> str:
    return COUNTRY_FLAGS.get(code, "")

# === дальше код можно оставить без изменений ===






























































































































































































































































