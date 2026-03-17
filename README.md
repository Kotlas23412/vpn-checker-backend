# VPN Checker Backend (FAST/ALL + WHITE/BLACK)

Автоматический бэкенд для проверки и сборки бесплатных VPN‑ключей (VLESS/VMess/Trojan/SS) с разбивкой на слои FAST/ALL, страны и WHITE/BLACK‑списки. [github](https://github.com/kort0881/vpn-checker-backend)

> Предупреждение: скрипт работает с публичными конфигами из открытых источников. Используйте на свой страх и риск.

## Возможности

- Сбор VLESS/VMess/Trojan/Shadowsocks‑ключей из нескольких GitHub‑репозиториев и URL. [github](https://github.com/kort0881/vpn-checker-backend)
- Удаление дублей, проверка доступности серверов по TCP/TLS/WebSocket и измерение пинга. [github](https://github.com/kort0881/vpn-checker-backend)
- Фильтрация мусорных/медленных ключей и сортировка по задержке. [perplexity](https://www.perplexity.ai/search/82d9fcc0-1d3f-4849-af0a-6371980d4d87)
- Разделение на слои FAST (топ по пингу) и ALL, отдельно для России (RU) и Европы (EURO). [perplexity](https://www.perplexity.ai/search/82d9fcc0-1d3f-4849-af0a-6371980d4d87)
- Подписи ключей с пингом, страной по‑русски и флагом, например:  
  `[…] 123ms Германия 🇩🇪 @vlesstrojan`. [perplexity](https://www.perplexity.ai/search/82d9fcc0-1d3f-4849-af0a-6371980d4d87)
- Разделение на WHITE (живые) и BLACK (упавшие) списки для RU и EURO. [perplexity](https://www.perplexity.ai/search/82d9fcc0-1d3f-4849-af0a-6371980d4d87)
- Генерация `subscriptions_list.txt` со всеми HTTP‑ссылками на списки — удобно кидать в клиенты как подписки. [perplexity](https://www.perplexity.ai/search/82d9fcc0-1d3f-4849-af0a-6371980d4d87)

## Как это работает

1. **Сбор ключей**  
   Скрипт забирает списки из `URLS_RU` и `URLS_MY`, конвертирует GitHub‑ссылки в `raw.githubusercontent.com` и вытаскивает строки, начинающиеся на `vless://`, `vmess://`, `trojan://`, `ss://`. [perplexity](https://www.perplexity.ai/search/82d9fcc0-1d3f-4849-af0a-6371980d4d87)

2. **Удаление дублей и лимит**  
   Дубликаты убираются по строке ключа, общее количество ограничивается `MAX_KEYS_TO_CHECK` для защиты от мусора. [perplexity](https://www.perplexity.ai/search/82d9fcc0-1d3f-4849-af0a-6371980d4d87)

3. **Кэш истории**  
   Для каждого ключа хранится история в `checked/history.json` (alive, latency, country, host, time). Свежие и живые записи берутся из кэша без повторной проверки. [perplexity](https://www.perplexity.ai/search/82d9fcc0-1d3f-4849-af0a-6371980d4d87)

4. **Проверка доступности и пинга**  
   Для новых ключей выполняется:  
   - парсинг `host:port`,  
   - определение страны (`get_country_fast`),  
   - отсев российских выходов из EURO‑пула (`is_russian_exit`),  
   - попытка подключения через TCP/TLS/WebSocket и измерение задержки в миллисекундах. [perplexity](https://www.perplexity.ai/search/82d9fcc0-1d3f-4849-af0a-6371980d4d87)

5. **Формирование подписей**  
   Для живых ключей формируется финальная строка вида:  
   `…#[123ms Германия 🇩🇪 @vlesstrojan]` — это удобно фильтровать и группировать сервера в графических клиентах по стране и пингу. [perplexity](https://www.perplexity.ai/search/82d9fcc0-1d3f-4849-af0a-6371980d4d87)

6. **FAST / ALL слои**  
   - После фильтра по пингу (`<= MAX_PING_MS`) ключи сортируются по задержке.  
   - Формируются списки:  
     - RU/EURO FAST — топ `FAST_LIMIT` по пингу;  
     - RU/EURO ALL — все живые ключи. [perplexity](https://www.perplexity.ai/search/82d9fcc0-1d3f-4849-af0a-6371980d4d87)
   - Файлы:  
     - `checked/RU_Best/ru_white_part1..4.txt` — RUSSIA (FAST);  
     - `checked/My_Euro/my_euro_part1..3.txt` — EUROPE (FAST);  
     - `checked/RU_Best/ru_white_all_part*.txt` — RUSSIA (ALL);  
     - `checked/My_Euro/my_euro_all_part*.txt` — EUROPE (ALL). [perplexity](https://www.perplexity.ai/search/82d9fcc0-1d3f-4849-af0a-6371980d4d87)

7. **WHITE / BLACK списки**  
   - WHITE = все живые ключи после проверки и фильтрации по пингу:  
     - `checked/RU_Best/ru_white_all_WHITE.txt`;  
     - `checked/My_Euro/my_euro_all_WHITE.txt`.  
   - BLACK = все ключи, которые не прошли проверку (ошибка подключения, таймаут и т.п.):  
     - `checked/RU_Best/ru_white_all_BLACK.txt`;  
     - `checked/My_Euro/my_euro_all_BLACK.txt`. [perplexity](https://www.perplexity.ai/search/82d9fcc0-1d3f-4849-af0a-6371980d4d87)

8. **subscriptions_list.txt**  
   Скрипт собирает все итоговые файлы в один `checked/subscriptions_list.txt` с HTTP‑ссылками на GitHub Raw. Этот файл удобно использовать как «каталог подписок» — просто скопировать нужный URL в клиент (V2Ray/Xray/Clash и т.п.). [perplexity](https://www.perplexity.ai/search/82d9fcc0-1d3f-4849-af0a-6371980d4d87)

## Использование локально

```bash
git clone https://github.com/kort0881/vpn-checker-backend.git
cd vpn-checker-backend
python main.py
```

После запуска:

- готовые списки будут в `checked/RU_Best` и `checked/My_Euro`;  
- файл `checked/subscriptions_list.txt` будет содержать ссылки, которые можно сразу импортировать в клиент как подписки. [perplexity](https://www.perplexity.ai/search/82d9fcc0-1d3f-4849-af0a-6371980d4d87)

## Автоматическое обновление (GitHub Actions)

В репозитории настроен workflow, который по расписанию:

- запускает `python main.py`;  
- коммитит обновлённые файлы `checked/*` в репозиторий. [github](https://github.com/kort0881/vpn-checker-backend)

Благодаря этому списки ключей и подписок обновляются автоматически без ручного вмешательства. [github](https://github.com/kort0881/vpn-checker-backend)
