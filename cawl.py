import os
import re
import sys
import time
import datetime
import unicodedata

try:
    import requests
except ImportError:
    print("Thiếu thư viện 'requests'. Vui lòng chạy: pip install requests")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup, NavigableString
except ImportError:
    print("Thiếu thư viện 'beautifulsoup4'. Vui lòng chạy: pip install beautifulsoup4")
    sys.exit(1)


URL_PATTERN = re.compile(r'https?://\S+')
SPECIAL_YAML_START = tuple('!&*?|>%@`"\'{}[],#')
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/124.0 Safari/537.36'
}

FIXED_IMAGE = 'https://banmaixanh.vercel.app/image/cover/0001-0878.jpg'
FIXED_WRITING = 'triet hoc duong pho'
FIXED_AUTHOR = 'nguyen dan nguyen'


def messages(msg_type, *args, return_string=False):
    messages_dict = {
        "welcome": "Công cụ cào dữ liệu từ web.archive.org sang Markdown, chuẩn hóa YAML Frontmatter.",
        "url-file-prompt": "Nhập đường dẫn tệp .txt chứa danh sách URL: ",
        "url-file-invalid": "Tệp {0} không tồn tại. Nhập lại: ",
        "url-file-empty": "Tệp {0} không chứa URL nào hợp lệ. Nhập lại: ",
        "output-dir-prompt": "Nhập thư mục lưu kết quả (mặc định 'output'): ",
        "processing": "Đang xử lý…",
        "fetch-error": "Không tải được nội dung trang",
        "no-article": "Không tìm thấy thẻ <article> hoặc nội dung rỗng",
        "skip-exist": "Đã tồn tại, bỏ qua",
        "save-success": "Đã lưu: {0}",
        "complete": "Tổng: {0} URL | Thành công: {1} | Bỏ qua: {2} | Thất bại: {3}.",
        "output-path": "Kết quả được lưu tại thư mục: {0}.",
        "prompt-next": (
            "Chọn tiếp theo:\n"
            "0: Cào tệp URL khác.\n"
            "1: Thoát ứng dụng.\n"
            "Vui lòng chọn: "
        ),
    }
    message = messages_dict.get(msg_type, "").format(*args)
    if return_string:
        return message
    print(message)


def log(counter, total, url, status):
    ts = datetime.datetime.now().strftime("%Y%m%d %H%M%S")
    print(f"{counter}/{total} | {ts} | {url} | {status}.")


def yaml_scalar(value):
    value = (value or '').strip()
    if value == '':
        return ''
    needs_quote = (
        ':' in value
        or value.startswith(SPECIAL_YAML_START)
        or value.endswith(':')
        or '\n' in value
    )
    if needs_quote:
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    return value


def slugify(text):
    text = (text or '').strip().lower()
    text = text.replace('đ', 'd').replace('Đ', 'd')
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text).strip('-')
    return text or 'untitled'


def remove_diacritics_lower(text):
    text = (text or '').strip().lower()
    text = text.replace('đ', 'd')
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def strip_urls(text):
    return URL_PATTERN.sub('', text or '')


def inline_to_md(node):
    parts = []
    for child in node.children:
        if isinstance(child, NavigableString):
            parts.append(str(child))
            continue
        name = child.name
        if name == 'br':
            parts.append('\n')
        elif name in ('strong', 'b'):
            inner = inline_to_md(child).strip()
            if inner:
                parts.append(f'**{inner}**')
        elif name in ('em', 'i'):
            inner = inline_to_md(child).strip()
            if inner:
                parts.append(f'*{inner}*')
        elif name == 'a':
            inner = inline_to_md(child).strip()
            if inner:
                parts.append(inner)
        elif name == 'img':
            continue
        elif name == 'code':
            inner = inline_to_md(child).strip()
            if inner:
                parts.append(f'`{inner}`')
        elif name in ('script', 'style', 'iframe', 'noscript', 'ins', 'form'):
            continue
        else:
            parts.append(inline_to_md(child))
    return ''.join(parts)


def table_to_md(table_node):
    rows = table_node.find_all('tr', recursive=True)
    if not rows:
        return ''
    md_rows = []
    for i, row in enumerate(rows):
        cells = row.find_all(['th', 'td'], recursive=False)
        cell_texts = [inline_to_md(cell).strip().replace('\n', ' ') for cell in cells]
        md_rows.append('| ' + ' | '.join(cell_texts) + ' |')
        if i == 0:
            md_rows.append('| ' + ' | '.join(['---'] * len(cells)) + ' |')
    return '\n'.join(md_rows)


def block_to_md(node):
    parts = []
    for child in node.children:
        if isinstance(child, NavigableString):
            text = str(child).strip()
            if text:
                parts.append(text)
            continue

        name = child.name

        if name in ('script', 'style', 'iframe', 'noscript', 'ins', 'form'):
            continue

        elif name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            level = int(name[1])
            text = inline_to_md(child).strip()
            if text:
                parts.append(f"{'#' * level} {text}")

        elif name == 'p':
            text = inline_to_md(child).strip()
            if text:
                parts.append(text)

        elif name == 'blockquote':
            inner_md = block_to_md(child).strip()
            if inner_md:
                quoted_lines = [f'> {line}' if line else '>' for line in inner_md.split('\n')]
                parts.append('\n'.join(quoted_lines))

        elif name in ('ul', 'ol'):
            items = []
            counter = 1
            for li in child.find_all('li', recursive=False):
                text = inline_to_md(li).strip()
                if not text:
                    continue
                if name == 'ul':
                    items.append(f'- {text}')
                else:
                    items.append(f'{counter}. {text}')
                    counter += 1
            if items:
                parts.append('\n'.join(items))

        elif name == 'pre':
            code_text = child.get_text()
            parts.append(f'```\n{code_text.strip()}\n```')

        elif name == 'img':
            continue

        elif name == 'hr':
            parts.append('---')

        elif name == 'table':
            table_md = table_to_md(child)
            if table_md:
                parts.append(table_md)

        else:
            inner = block_to_md(child).strip()
            if inner:
                parts.append(inner)

    return '\n\n'.join(p for p in parts if p)


def fetch_html(url, retries=3, timeout=25):
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=REQUEST_HEADERS, timeout=timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except requests.RequestException:
            if attempt == retries:
                return None
            time.sleep(2 * attempt)
    return None


def parse_article(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.find('article')
    if article is None:
        return None

    for junk in article.find_all(['script', 'style', 'iframe', 'noscript']):
        junk.decompose()

    title_tag = article.find('h1', class_='entry-title')
    title = title_tag.get_text(strip=True) if title_tag else ''

    time_tag = article.find('time', class_='entry-time')
    pub_datetime = ''
    if time_tag:
        pub_datetime = (time_tag.get('datetime') or time_tag.get_text(strip=True) or '').strip()
    if pub_datetime.endswith('+00:00'):
        pub_datetime = pub_datetime[:-6] + 'Z'

    tags = []
    tags_tag = article.find(class_='entry-tags')
    if tags_tag:
        for a_tag in tags_tag.find_all('a'):
            tag_text = a_tag.get_text(strip=True)
            if tag_text and tag_text not in tags:
                tags.append(tag_text)
    if not tags:
        for a_tag in article.find_all('a', attrs={'rel': 'tag'}):
            tag_text = a_tag.get_text(strip=True)
            if tag_text and tag_text not in tags:
                tags.append(tag_text)
    tags = [remove_diacritics_lower(tag) for tag in tags]

    description = ''
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        description = meta_desc['content'].strip()
    if not description:
        meta_og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if meta_og_desc and meta_og_desc.get('content'):
            description = meta_og_desc['content'].strip()

    content_tag = article.find(class_='entry-content')
    content_md = ''
    if content_tag:
        for junk in content_tag.find_all(['script', 'style', 'iframe', 'ins', 'form']):
            junk.decompose()
        for junk in content_tag.find_all(id='fb-root'):
            junk.decompose()
        content_md = block_to_md(content_tag).strip()
    content_md = strip_urls(content_md)

    return {
        'url': url,
        'title': title,
        'pubDatetime': pub_datetime,
        'author': FIXED_AUTHOR,
        'writing': FIXED_WRITING,
        'tags': tags,
        'image': FIXED_IMAGE,
        'description': description,
        'content': content_md,
    }


def build_frontmatter(data):
    lines = ['---']
    lines.append(f"pubDatetime: {data['pubDatetime']}")
    lines.append(f"title: {yaml_scalar(data['title'])}")
    lines.append(f"description: {yaml_scalar(data['description'])}")
    lines.append(f"image: {data['image']}")
    if data['tags']:
        lines.append('tags:')
        for tag in data['tags']:
            lines.append(f'  - {yaml_scalar(tag)}')
    else:
        lines.append('tags: []')
    lines.append(f"writing: {yaml_scalar(data.get('writing', ''))}")
    lines.append(f"author: {yaml_scalar(data['author'])}")
    lines.append('---')
    return '\n'.join(lines)


def build_output_path(title, output_dir):
    filename = slugify(title) + '.md'
    return os.path.join(output_dir, filename)


def save_markdown(data, filepath):
    frontmatter = build_frontmatter(data)
    body = data['content'].strip()
    full_md = f"{frontmatter}\n\n{body}\n"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_md)
    return filepath


def read_urls(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    return urls


def process_urls(urls, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    total = len(urls)
    success = 0
    skipped = 0
    failed = 0

    for index, url in enumerate(urls, start=1):
        html = fetch_html(url)
        if not html:
            failed += 1
            log(index, total, url, messages("fetch-error", return_string=True))
            continue

        data = parse_article(html, url)
        if not data or not data['content']:
            failed += 1
            log(index, total, url, messages("no-article", return_string=True))
            continue

        filepath = build_output_path(data['title'], output_dir)
        if os.path.exists(filepath):
            skipped += 1
            log(index, total, url, messages("skip-exist", return_string=True))
            continue

        save_markdown(data, filepath)
        success += 1
        log(index, total, url, messages("save-success", filepath, return_string=True))

    return total, success, skipped, failed


def get_url_file():
    file_path = input(messages("url-file-prompt", return_string=True)).strip().strip('"')
    while not os.path.isfile(file_path):
        file_path = input(messages("url-file-invalid", file_path, return_string=True)).strip().strip('"')

    urls = read_urls(file_path)
    while not urls:
        file_path = input(messages("url-file-empty", file_path, return_string=True)).strip().strip('"')
        while not os.path.isfile(file_path):
            file_path = input(messages("url-file-invalid", file_path, return_string=True)).strip().strip('"')
        urls = read_urls(file_path)

    return urls


def get_output_dir():
    output_dir = input(messages("output-dir-prompt", return_string=True)).strip().strip('"')
    return output_dir or "output"


def main():
    while True:
        try:
            messages("welcome")

            urls = get_url_file()
            output_dir = get_output_dir()

            messages("processing")
            total, success, skipped, failed = process_urls(urls, output_dir)

            messages("complete", total, success, skipped, failed)
            print(messages("output-path", os.path.abspath(output_dir), return_string=True))

            next_choice = input(messages("prompt-next", return_string=True)).strip()
            if next_choice == "1":
                sys.exit(0)

        except (EOFError, KeyboardInterrupt):
            sys.exit(0)


if __name__ == "__main__":
    main()
