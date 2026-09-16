"""Замер скорости интернета: N последовательных GET-запросов к URL, скорость в МБ/с."""

import argparse
import sys
import time
import urllib.error
import urllib.request

MB = 1024 * 1024
CHUNK = 64 * 1024


def fetch(url, timeout):
    """Один запрос. Возвращает (время_сек, байты) или None при ошибке."""
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                print(f"  HTTP {resp.status}, пропуск", file=sys.stderr)
                return None
            size = 0
            while chunk := resp.read(CHUNK):
                size += len(chunk)
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        print(f"  ошибка: {e}", file=sys.stderr)
        return None
    return time.perf_counter() - start, size


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="URL тяжёлого файла (картинки)")
    parser.add_argument("-n", type=int, default=10, help="число запросов (по умолчанию 10)")
    parser.add_argument("-t", "--timeout", type=int, default=30, help="таймаут запроса, с (по умолчанию 30)")
    args = parser.parse_args()

    times, total_bytes = [], 0
    try:
        for i in range(1, args.n + 1):
            result = fetch(args.url, args.timeout)
            if result is None:
                continue
            t, size = result
            times.append(t)
            total_bytes += size
            print(f"Запрос {i:>2}/{args.n}: {t:6.2f} с, {size / MB:8.2f} МБ, {size / t / MB:6.2f} МБ/с")
    except KeyboardInterrupt:
        print("\nПрервано")
        sys.exit(130)

    if not times:
        print("Все запросы не удались", file=sys.stderr)
        sys.exit(1)

    total_time = sum(times)
    speed = total_bytes / total_time / MB
    print(f"\nЗапросов: {len(times)}/{args.n}")
    print(f"Среднее время запроса: {total_time / len(times):.2f} с")
    print(f"Скачано: {total_bytes / MB:.2f} МБ за {total_time:.2f} с")
    print(f"Скорость: {speed:.2f} МБ/с")


if __name__ == "__main__":
    main()
