VPN Checker Backend (FAST/ALL + WHITE/BLACK)
Автоматический бэкенд для проверки и сборки бесплатных VPN‑ключей (VLESS/VMess/Trojan/SS) с разбивкой на слои FAST/ALL, страны и WHITE/BLACK‑списки.
​

Предупреждение: скрипт работает с публичными конфигами из открытых источников. Используйте на свой страх и риск.

Возможности
Сбор VLESS/VMess/Trojan/Shadowsocks‑ключей из нескольких GitHub‑репозиториев и URL.
​

Удаление дублей, проверка доступности серверов по TCP/TLS/WebSocket и измерение пинга.
​

Фильтрация мусорных/медленных ключей и сортировка по задержке.
​

Разделение на слои FAST (топ по пингу) и ALL, отдельно для России (RU) и Европы (EURO).
​

Подписи ключей с пингом, страной по‑русски и флагом, например:
[…] 123ms Германия 🇩🇪 @vlesstrojan.
​

Разделение на WHITE (живые) и BLACK (упавшие) списки для RU и EURO.
​

Генерация subscriptions_list.txt со всеми HTTP‑ссылками на списки — удобно кидать в клиенты как подписки.
​

Как это работает
Сбор ключей
Скрипт забирает списки из URLS_RU и URLS_MY, конвертирует GitHub‑ссылки в raw.githubusercontent.com и вытаскивает строки, начинающиеся на vless://, vmess://, trojan://, ss://.
​

Удаление дублей и лимит
Дубликаты убираются по строке ключа, общее количество ограничивается MAX_KEYS_TO_CHECK для защиты от мусора.
​

Кэш истории
Для каждого ключа хранится история в checked/history.json (alive, latency, country, host, time). Свежие и живые записи берутся из кэша без повторной проверки.
​

Проверка доступности и пинга
Для новых ключей выполняется:

парсинг host:port,

определение страны (get_country_fast),

отсев российских выходов из EURO‑пула (is_russian_exit),

попытка подключения через TCP/TLS/WebSocket и измерение задержки в миллисекундах.
​

Формирование подписей
Для живых ключей формируется финальная строка вида:
…#[123ms Германия 🇩🇪 @vlesstrojan] — это удобно фильтровать и группировать сервера в графических клиентах по стране и пингу.
​

FAST / ALL слои

После фильтра по пингу (<= MAX_PING_MS) ключи сортируются по задержке.

Формируются списки:

RU/EURO FAST — топ FAST_LIMIT по пингу;

RU/EURO ALL — все живые ключи.
​

Файлы:

checked/RU_Best/ru_white_part1..4.txt — RUSSIA (FAST);

checked/My_Euro/my_euro_part1..3.txt — EUROPE (FAST);

checked/RU_Best/ru_white_all_part*.txt — RUSSIA (ALL);

checked/My_Euro/my_euro_all_part*.txt — EUROPE (ALL).
​

WHITE / BLACK списки

WHITE = все живые ключи после проверки и фильтрации по пингу:

checked/RU_Best/ru_white_all_WHITE.txt;

checked/My_Euro/my_euro_all_WHITE.txt.

BLACK = все ключи, которые не прошли проверку (ошибка подключения, таймаут и т.п.):

checked/RU_Best/ru_white_all_BLACK.txt;

checked/My_Euro/my_euro_all_BLACK.txt.
​

subscriptions_list.txt
Скрипт собирает все итоговые файлы в один checked/subscriptions_list.txt с HTTP‑ссылками на GitHub Raw. Этот файл удобно использовать как «каталог подписок» — просто скопировать нужный URL в клиент (V2Ray/Xray/Clash и т.п.).
​

Использование локально
bash
git clone https://github.com/kort0881/vpn-checker-backend.git
cd vpn-checker-backend
python main.py
После запуска:

готовые списки будут в checked/RU_Best и checked/My_Euro;

файл checked/subscriptions_list.txt будет содержать ссылки, которые можно сразу импортировать в клиент как подписки.
​

Автоматическое обновление (GitHub Actions)
В репозитории настроен workflow, который по расписанию:

запускает python main.py;

коммитит обновлённые файлы checked/* в репозиторий.
​

Благодаря этому списки ключей и подписок обновляются автоматически без ручного вмешательства.
​
