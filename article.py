import os
import re
import sys
import time
import datetime
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Thiếu thư viện 'requests'. Vui lòng chạy: pip install requests")
    sys.exit(1)


CDX_ENDPOINT = "https://web.archive.org/cdx/search/cdx"
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/124.0 Safari/537.36'
}

ARTICLE_PATH_PATTERN = re.compile(r'^/\d{4}/\d{2}/\d{2}/[^/]+/?$')
EXCLUDE_KEYWORDS = (
    '/tag/', '/category/', '/author/', '/feed', '/page/', '/wp-',
    '/xmlrpc.php', '/comment-page-', '/embed', '/attachment/', '/trackback',
    '/sitemap', '/wp-json',
)


def messages(msg_type, *args, return_string=False):
    messages_dict = {
        "welcome": "Công cụ thu thập URL bài viết từ Wayback Machine (CDX Server API).",
        "domain-prompt": "Nhập domain cần thu thập (ví dụ: triethocduongpho.com): ",
        "domain-invalid": "Domain không hợp lệ. Nhập lại: ",
        "from-prompt": "Nhập mốc thời gian bắt đầu, định dạng YYYYMMDD (mặc định 20150101): ",
        "to-prompt": "Nhập mốc thời gian kết thúc, định dạng YYYYMMDD (Enter để dùng hôm nay): ",
        "output-prompt": "Nhập đường dẫn tệp .txt để lưu danh sách URL (mặc định 'urls.txt'): ",
        "counting-pages": "Đang xác định tổng số trang dữ liệu trên CDX Server…",
        "pages-found": "Tổng số trang CDX cần tải: {0}.",
        "fetch-page-error": "Lỗi tải trang {0}: {1}.",
        "filtering": "Đang lọc URL bài viết…",
        "result-summary": "Tổng capture thô: {0} | Sau lọc bài viết (mọi phiên bản): {1}.",
        "saved": "Đã lưu {0} URL vào tệp: {1}.",
        "no-result": "Không tìm thấy URL bài viết nào phù hợp trong khoảng thời gian đã chọn.",
        "prompt-next": (
            "Chọn tiếp theo:\n"
            "0: Thu thập domain khác.\n"
            "1: Thoát ứng dụng.\n"
            "Vui lòng chọn: "
        ),
    }
    message = messages_dict.get(msg_type, "").format(*args)
    if return_string:
        return message
    print(message)


def log(counter, total, label, status):
    ts = datetime.datetime.now().strftime("%Y%m%d %H%M%S")
    print(f"{counter}/{total} | {ts} | {label} | {status}.")


def normalize_domain(domain):
    domain = domain.strip()
    domain = re.sub(r'^https?://', '', domain, flags=re.IGNORECASE)
    domain = domain.strip('/')
    return domain


def strip_query_and_fragment(url):
    parsed = urlparse(url)
    cleaned = parsed._replace(query='', fragment='')
    return cleaned.geturl()


def build_cdx_params(domain, date_from, date_to, page=None, show_num_pages=False):
    params = {
        'url': domain,
        'matchType': 'domain',
        'filter': ['statuscode:200', 'mimetype:text/html'],
        'from': date_from,
        'to': date_to,
    }
    if show_num_pages:
        params['showNumPages'] = 'true'
    else:
        params['output'] = 'json'
        params['fl'] = 'timestamp,original,statuscode,mimetype,length'
        if page is not None:
            params['page'] = page
    return params


def request_with_retries(params, retries=3, timeout=60):
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(CDX_ENDPOINT, params=params, headers=REQUEST_HEADERS, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException:
            if attempt == retries:
                return None
            time.sleep(2 * attempt)
    return None


def get_num_pages(domain, date_from, date_to):
    params = build_cdx_params(domain, date_from, date_to, show_num_pages=True)
    response = request_with_retries(params)
    if response is None:
        return 1
    text = response.text.strip()
    try:
        return max(1, int(text))
    except ValueError:
        return 1


def fetch_cdx_page(domain, date_from, date_to, page):
    params = build_cdx_params(domain, date_from, date_to, page=page)
    response = request_with_retries(params)
    if response is None:
        return None
    try:
        data = response.json()
    except ValueError:
        return []
    if not data or len(data) < 2:
        return []
    header = data[0]
    return [dict(zip(header, row)) for row in data[1:]]


def is_article_url(pure_url):
    parsed = urlparse(pure_url)
    lowered = parsed.path.lower()
    if any(keyword in lowered for keyword in EXCLUDE_KEYWORDS):
        return False
    return bool(ARTICLE_PATH_PATTERN.match(parsed.path))


def dedupe_exact(records):
    seen = set()
    unique_records = []
    for record in records:
        key = (record['timestamp'], record['original'])
        if key in seen:
            continue
        seen.add(key)
        unique_records.append(record)
    return unique_records


def build_wayback_url(record):
    return f"https://web.archive.org/web/{record['timestamp']}/{record['original']}"


def collect_urls(domain, date_from, date_to):
    messages("counting-pages")
    total_pages = get_num_pages(domain, date_from, date_to)
    messages("pages-found", total_pages)

    all_records = []
    for page in range(total_pages):
        log(page + 1, total_pages, f"page={page}", "đang tải")
        records = fetch_cdx_page(domain, date_from, date_to, page)
        if records is None:
            log(page + 1, total_pages, f"page={page}", "thất bại")
            continue
        all_records.extend(records)
        time.sleep(0.5)

    messages("filtering")
    for record in all_records:
        record['original'] = strip_query_and_fragment(record['original'])

    article_records = [r for r in all_records if is_article_url(r['original'])]
    article_records = dedupe_exact(article_records)
    article_records.sort(key=lambda r: (r['original'], r['timestamp']))

    messages("result-summary", len(all_records), len(article_records))
    return article_records


def save_urls(records, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(build_wayback_url(record) + '\n')


def get_domain():
    domain = input(messages("domain-prompt", return_string=True)).strip()
    while not domain:
        domain = input(messages("domain-invalid", return_string=True)).strip()
    return normalize_domain(domain)


def get_date_range():
    date_from = input(messages("from-prompt", return_string=True)).strip() or "20150101"
    date_to = input(messages("to-prompt", return_string=True)).strip() or datetime.datetime.now().strftime("%Y%m%d")
    return date_from, date_to


def get_output_path():
    output_path = input(messages("output-prompt", return_string=True)).strip().strip('"')
    return output_path or "urls.txt"


def main():
    while True:
        try:
            messages("welcome")

            domain = get_domain()
            date_from, date_to = get_date_range()
            output_path = get_output_path()

            records = collect_urls(domain, date_from, date_to)
            if not records:
                messages("no-result")
            else:
                save_urls(records, output_path)
                messages("saved", len(records), os.path.abspath(output_path))

            next_choice = input(messages("prompt-next", return_string=True)).strip()
            if next_choice == "1":
                sys.exit(0)

        except (EOFError, KeyboardInterrupt):
            sys.exit(0)


if __name__ == "__main__":
    main()
