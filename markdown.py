#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Công cụ cập nhật tệp Markdown – phát triển bởi @nhavantuonglai.
Hỗ trợ: info@nhavan.vn.
"""

import os
import sys
import glob
import random
import datetime
import re
import requests
import webbrowser
import shutil
from pathlib import Path


# ====================== MESSAGES ======================

def messages(msg_type, *args, return_string=False):
    messages_dict = {
        "welcome": "Công cụ cập nhật tệp Markdown, phát triển bởi @nhavantuonglai. Hỗ trợ: info@nhavan.vn.",
        "features": (
            "Chọn tính năng:\n"
            "1. Thay đổi date.\n"
            "2. Thay đổi description.\n"
            "3. Thay đổi cover và figure cuối trang.\n"
            "4. Thay đổi figure.\n"
            "5. Thêm tags mới (tên tệp).\n"
            "6. Lọc và move theo tag.\n"
            "7. Xóa liên kết theo danh sách URL.\n"
            "0. Thoát ứng dụng."
        ),
        "feature-prompt": "Vui lòng chọn: ",
        "feature-invalid": "Lựa chọn không hợp lệ. Chọn lại: ",
        "directory-prompt": "Nhập folder (mặc định hiện tại): ",
        "directory-invalid": "Folder {0} không tồn tại. Nhập lại: ",
        "url-file-prompt": "Nhập đường dẫn tệp url.txt: ",
        "url-file-invalid": "Tệp {0} không tồn tại. Nhập lại: ",
        "url-fetch-error": "Không tải được danh sách ảnh.",
        "processing": "Đang xử lý…",
        "no-frontmatter": "Không tìm thấy frontmatter trong {0}.",
        "no-figure": "Không có figure cần cập nhật trong {0}.",
        "file-error": "Lỗi xử lý {0}: {1}.",
        "file-zero": "Không tìm thấy tệp .md nào trong {0}.",
        "complete": "Tổng: {0} tệp | Thành công: {1} | Thất bại: {2}.",
        "tag-prompt": "Nhập tag cần lọc (1 tag duy nhất): ",
        "move-folder-prompt": "Nhập folder đích (tạo mới nếu chưa tồn tại): ",
        "no-matching-files": "Không tìm thấy tệp nào có tag \"{0}\".",
        "prompt-next": (
            "Chọn tiếp theo:\n"
            "0: Thao tác lại.\n"
            "1: Truy cập nhavan.vn.\n"
            "2: Thoát ứng dụng.\n"
            "Vui lòng chọn: "
        ),
    }
    message = messages_dict.get(msg_type, "").format(*args)
    if return_string:
        return message
    print(message)


# ====================== HÀM HỖ TRỢ CHUNG ======================

def get_md_files(directory):
    """Lấy danh sách toàn bộ tệp .md, xáo trộn ngẫu nhiên."""
    files = glob.glob(os.path.join(directory, '**', '*.md'), recursive=True)
    random.shuffle(files)
    return files


def log(counter, fname, feature_name, status):
    ts = datetime.datetime.now().strftime("%Y%m%d %H%M%S")
    print(f"{counter} | {ts} | {fname} | {feature_name} | {status}.")


def fetch_image_urls():
    """Tải danh sách URL ảnh từ CDN."""
    url = "https://banmaixanh.vercel.app/film.txt"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        urls = [line.strip() for line in response.text.splitlines() if line.strip()]
        return urls if urls else None
    except Exception:
        messages("url-fetch-error")
        return None


def read_frontmatter(file_path):
    """Đọc và trả về (content, frontmatter_string, fm_span) hoặc None."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    m = re.search(r'^---\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
    if not m:
        return None
    return content, m.group(1), m.span()


def write_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)





# ====================== CHỨC NĂNG 1: THAY ĐỔI DATE ======================

def update_date(file_path, new_dt):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if len(lines) > 1:
            lines[1] = f"pubDatetime: {new_dt}\n"
            write_file(file_path, ''.join(lines))
            return True
        return False
    except Exception as e:
        messages("file-error", file_path, str(e))
        return False


def process_date(directory):
    files = get_md_files(directory)
    if not files:
        messages("file-zero", directory)
        return 0, 0, 0

    now = datetime.datetime.now()
    dates = [now - datetime.timedelta(days=i + 1) for i in range(len(files))]
    total, success = len(files), 0

    for i, fpath in enumerate(files):
        new_dt = dates[i].strftime("%Y-%m-%dT10:10:00Z")
        ok = update_date(fpath, new_dt)
        log(i + 1, os.path.basename(fpath), "date", "thành công" if ok else "thất bại")
        if ok:
            success += 1

    return total, success, total - success


# ====================== CHỨC NĂNG 2: THAY ĐỔI DESCRIPTION ======================

def extract_body_text(content):
    """
    Loại bỏ frontmatter và các thẻ HTML/Markdown đặc biệt,
    trả về văn bản thuần để trích description.
    """
    # Xóa frontmatter
    body = re.sub(r'^---\n.*?\n---\n?', '', content, flags=re.DOTALL)
    # Xóa thẻ figure/img
    body = re.sub(r'<figure\b.*?</figure>', '', body, flags=re.DOTALL | re.IGNORECASE)
    # Xóa các thẻ HTML còn lại
    body = re.sub(r'<[^>]+>', '', body)
    # Xóa cú pháp Markdown (in đậm, in nghiêng, tiêu đề, gạch đầu dòng, số thứ tự)
    body = re.sub(r'[*_#`>~\-]+', ' ', body)
    # Xóa liên kết Markdown
    body = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', body)
    return body


def filter_description(text):
    """Chỉ giữ chữ cái, số, khoảng trắng, dấu phẩy và dấu chấm."""
    return ''.join(c for c in text if c.isalpha() or c.isdigit() or c in ' ,.')


def pick_description_snippet(body, min_len=150, max_len=155):
    """
    Chọn ngẫu nhiên 1 đoạn 150–155 ký tự (sau khi lọc ký tự hợp lệ)
    từ văn bản body. Kết quả phải bắt đầu bằng chữ hoa và kết thúc bằng dấu chấm.
    Trả về chuỗi đã chuẩn hóa, hoặc None nếu không đủ nội dung.
    """
    filtered = filter_description(body)
    # Chuẩn hóa khoảng trắng
    filtered = re.sub(r' +', ' ', filtered).strip()

    if len(filtered) < min_len:
        return None

    # Các vị trí bắt đầu hợp lệ: ký tự là chữ hoa
    max_start = len(filtered) - min_len
    candidates = [i for i in range(max_start + 1) if filtered[i].isupper()]
    if not candidates:
        candidates = list(range(max_start + 1))

    random.shuffle(candidates)

    for start in candidates:
        # Lấy đoạn dài hơn max_len một chút để tìm điểm kết thúc
        chunk = filtered[start:start + max_len + 30]

        # Tìm dấu chấm trong phạm vi [min_len, max_len] tính từ start
        best = None
        for offset in range(min_len - 1, min(max_len, len(chunk))):
            if chunk[offset] == '.':
                best = offset + 1  # bao gồm dấu chấm
                break

        if best is None:
            # Không có dấu chấm → cắt tại max_len và tự thêm
            snippet = chunk[:max_len].rstrip() + '.'
        else:
            snippet = chunk[:best]

        # Đảm bảo bắt đầu bằng chữ hoa
        snippet = snippet.strip()
        if not snippet:
            continue
        snippet = snippet[0].upper() + snippet[1:]

        # Kiểm tra độ dài sau khi xử lý
        if min_len <= len(snippet) <= max_len + 5:
            return snippet

    # Fallback: lấy đoạn đầu tiên đủ dài
    snippet = filtered[:max_len].rstrip() + '.'
    snippet = snippet[0].upper() + snippet[1:]
    return snippet


def update_description(file_path):
    """
    Trích 1 đoạn ngẫu nhiên 150–155 ký tự từ nội dung tệp,
    chuẩn hóa và ghi vào trường description trong frontmatter.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        body = extract_body_text(content)
        snippet = pick_description_snippet(body)
        if not snippet:
            return False

        lines = content.splitlines(keepends=True)
        for i, line in enumerate(lines):
            if line.startswith('description:'):
                lines[i] = f"description: {snippet}\n"
                write_file(file_path, ''.join(lines))
                return True
        return False

    except Exception as e:
        messages("file-error", file_path, str(e))
        return False


def process_description(directory):
    files = get_md_files(directory)
    if not files:
        messages("file-zero", directory)
        return 0, 0, 0

    total, success = len(files), 0

    for i, fpath in enumerate(files):
        ok = update_description(fpath)
        log(i + 1, os.path.basename(fpath), "description", "thành công" if ok else "thất bại")
        if ok:
            success += 1

    return total, success, total - success


# ====================== CHỨC NĂNG 3: THAY ĐỔI COVER VÀ FIGURE CUỐI TRANG ======================

def update_cover_and_last_figure(file_path, url_cover, url_figure):
    """
    Cập nhật đồng thời:
      - Trường image: trong frontmatter (cover).
      - src của <figure> cuối cùng trong nội dung.
    Đảm bảo url_cover != url_figure.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        changed = False

        # Cập nhật cover (dòng index 4, 0-based)
        if len(lines) > 4 and lines[4].startswith('image:'):
            lines[4] = f"image: {url_cover}\n"
            changed = True

        # Tìm figure cuối cùng và cập nhật src
        for j in range(len(lines) - 1, -1, -1):
            if lines[j].strip().startswith('<figure><img src='):
                lines[j] = re.sub(r'src="[^"]*"', f'src="{url_figure}"', lines[j])
                changed = True
                break

        if changed:
            write_file(file_path, ''.join(lines))
        return changed

    except Exception as e:
        messages("file-error", file_path, str(e))
        return False


def process_cover_and_figure(directory):
    files = get_md_files(directory)
    if not files:
        messages("file-zero", directory)
        return 0, 0, 0

    urls = fetch_image_urls()
    if not urls or len(urls) < 2:
        messages("url-fetch-error")
        return len(files), 0, len(files)

    total, success = len(files), 0

    for i, fpath in enumerate(files):
        # Chọn 2 URL khác nhau cho cover và figure
        url_cover = urls[i % len(urls)]
        url_figure = urls[(i + len(urls) // 2) % len(urls)]
        # Đảm bảo 2 URL không trùng nhau
        if url_cover == url_figure:
            url_figure = urls[(i + 1) % len(urls)]

        ok = update_cover_and_last_figure(fpath, url_cover, url_figure)
        log(i + 1, os.path.basename(fpath), "cover + figure cuối", "thành công" if ok else "thất bại")
        if ok:
            success += 1

    return total, success, total - success


# ====================== CHỨC NĂNG 4: THAY ĐỔI FIGURE ======================

def extract_title_and_tags(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        m = re.search(r'^---\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
        if not m:
            messages("no-frontmatter", file_path)
            return None, None
        fm = m.group(1)
        title_m = re.search(r'^title:\s*(.+)$', fm, re.MULTILINE)
        if not title_m:
            return None, None
        title = title_m.group(1).strip()
        if not title.endswith(('.', '!', '?')):
            title += '.'
        tags_m = re.search(r'^tags:\s*\n((?:\s*-\s*.+\n?)+)', fm, re.MULTILINE)
        tags = re.findall(r'^\s*-\s*(.+)', tags_m.group(1), re.MULTILINE) if tags_m else []
        return title, [t.strip() for t in tags]
    except Exception as e:
        messages("file-error", file_path, str(e))
        return None, None


def format_alt(title, tags, used):
    while True:
        num = f"{random.randint(1, 999):03d}"
        if num not in used:
            used.add(num)
            break
    if not tags:
        return f"{title} {num}"
    if len(tags) == 1:
        return f"{title} {num} – {tags[0]}."
    return f"{title} {num} – {', '.join(tags[:-1] + [tags[-1] + '.'])}"


def update_figures(content, title, tags):
    used = set()

    def clean_title(t):
        return re.sub(r'\.*\s*$', '', t.strip())

    def replace(m):
        img = m.group(1).strip()
        src_m = re.search(r'\bsrc\s*=\s*"(.*?)"', img, re.IGNORECASE)
        src = src_m.group(1) if src_m else ""
        ct = clean_title(title)
        alt = format_alt(ct, tags, used)
        if not alt.endswith('.'):
            alt += '.'
        figcaption = ct + '.'
        return (
            f'<figure><img src="{src}" alt="{alt}" title="{ct}" '
            f'height="100%" width="100%" loading="lazy">'
            f'<figcaption>{figcaption}</figcaption></figure>'
        )

    pattern = r'<figure\b[^>]*>.*?<\s*img\b([^>]+?)>.*?</figure>'
    return re.sub(pattern, replace, content, flags=re.DOTALL | re.IGNORECASE)


def process_figures(directory):
    files = get_md_files(directory)
    if not files:
        messages("file-zero", directory)
        return 0, 0, 0

    total, success = len(files), 0

    for i, fpath in enumerate(files):
        title, tags = extract_title_and_tags(fpath)
        ok = False
        if title:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            updated = update_figures(content, title, tags)
            if updated != content:
                write_file(fpath, updated)
                ok = True
            else:
                messages("no-figure", fpath)
        log(i + 1, os.path.basename(fpath), "figure", "thành công" if ok else "thất bại")
        if ok:
            success += 1

    return total, success, total - success


# ====================== CHỨC NĂNG 5: THÊM TAG MỚI (TÊN TỆP) ======================

def add_filename_tag(file_path):
    """
    Nếu tên tệp (stem) chưa có trong danh sách tags, thêm vào cuối block tags.
    """
    stem = Path(file_path).stem.strip()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        m = re.search(r'^---\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
        if not m:
            messages("no-frontmatter", file_path)
            return False

        fm = m.group(1)
        tags_m = re.search(r'^tags:\s*\n((?:\s*-\s*.+\n?)+)', fm, re.MULTILINE)
        if not tags_m:
            return False

        existing_tags = re.findall(r'^\s*-\s*(.+?)(?:\n|$)', tags_m.group(1), re.MULTILINE)
        existing_tags = [t.strip().lower() for t in existing_tags]

        if stem.lower() in existing_tags:
            return False  # Tag đã tồn tại

        # Chèn tag mới vào cuối block tags (trước dòng tiếp theo không phải tag)
        tags_block_end = m.start(1) + tags_m.end(1) - (m.start() + 4)  # vị trí tương đối

        # Tìm vị trí cuối của block tags trong content gốc
        tags_block_match = re.search(r'(^tags:\s*\n(?:\s*-\s*.+\n?)+)', content, re.MULTILINE)
        if not tags_block_match:
            return False

        insert_pos = tags_block_match.end()
        new_content = content[:insert_pos] + f"  - {stem}\n" + content[insert_pos:]
        write_file(file_path, new_content)
        return True

    except Exception as e:
        messages("file-error", file_path, str(e))
        return False


def process_add_tag(directory):
    files = get_md_files(directory)
    if not files:
        messages("file-zero", directory)
        return 0, 0, 0

    total, success = len(files), 0

    for i, fpath in enumerate(files):
        ok = add_filename_tag(fpath)
        log(i + 1, os.path.basename(fpath), "thêm tag", "thành công" if ok else "đã có hoặc thất bại")
        if ok:
            success += 1

    return total, success, total - success


# ====================== CHỨC NĂNG 6: LỌC VÀ MOVE THEO TAG ======================

def parse_tags(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        m = re.search(r'^---\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
        if not m:
            return []
        fm = m.group(1)
        tags_m = re.search(r'^tags:\s*\n((?:\s*-\s*.+\n?)+)', fm, re.MULTILINE)
        if not tags_m:
            return []
        tags = re.findall(r'^\s*-\s*(.+?)(?:\n|$)', tags_m.group(1), re.MULTILINE)
        return [t.strip() for t in tags]
    except Exception:
        return []


def filter_and_move_files(directory, input_tag, target_folder):
    files = glob.glob(os.path.join(directory, '**', '*.md'), recursive=True)
    if not files:
        messages("file-zero", directory)
        return 0, 0, 0

    os.makedirs(target_folder, exist_ok=True)
    input_tag_lower = input_tag.lower().strip()
    matching = [f for f in files if input_tag_lower in {t.lower() for t in parse_tags(f)}]

    if not matching:
        messages("no-matching-files", input_tag)
        return 0, 0, 0

    random.shuffle(matching)
    total, success, counter = len(matching), 0, 1

    for fpath in matching:
        fname = os.path.basename(fpath)
        try:
            dest = os.path.join(target_folder, fname)
            if os.path.exists(dest):
                base, ext = os.path.splitext(fname)
                dest = os.path.join(target_folder, f"{base}_{counter}{ext}")
            shutil.move(fpath, dest)
            log(counter, fname, "lọc & move", "thành công")
            success += 1
        except Exception as e:
            log(counter, fname, "lọc & move", f"thất bại: {e}")
        counter += 1

    return total, success, total - success


# ====================== CHỨC NĂNG 7: XÓA LIÊN KẾT THEO DANH SÁCH URL ======================

def load_urls_to_remove(url_file):
    """Đọc url.txt, trả về set các URL cần xóa (đã chuẩn hóa)."""
    urls = set()
    path = Path(url_file)
    if not path.is_file():
        return urls
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    cleaned = line.rstrip('/').lower()
                    if cleaned:
                        urls.add(cleaned)
        print(f"Đã đọc {len(urls)} URL cần loại bỏ từ {url_file}.")
    except Exception as e:
        print(f"Lỗi khi đọc {url_file}: {e}")
    return urls


def remove_links_by_url_list(file_path, urls_to_remove):
    """
    Xóa các liên kết Markdown [text](url) nếu URL khớp với danh sách.
    Ảnh ![text](url) được bỏ qua. Trả về True nếu tệp có thay đổi.
    """
    path = Path(file_path)
    if not path.is_file() or path.suffix.lower() != '.md':
        return False
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        def repl(m):
            url = m.group(2).strip().rstrip('/').lower()
            if any(url == target or url.endswith('/' + target) for target in urls_to_remove):
                return m.group(1)
            return m.group(0)

        pattern = r'(?<!\!)\[([^\]]+)\]\(([^)]+)\)'
        new_content = re.sub(pattern, repl, content)

        if new_content == content:
            return False

        write_file(file_path, new_content)
        return True

    except Exception as e:
        messages("file-error", file_path, str(e))
        return False


def process_remove_links(directory, url_file):
    urls_to_remove = load_urls_to_remove(url_file)
    if not urls_to_remove:
        print("Không có URL nào để loại bỏ. Kết thúc.")
        return 0, 0, 0

    files = get_md_files(directory)
    if not files:
        messages("file-zero", directory)
        return 0, 0, 0

    total, success, counter = len(files), 0, 1

    for fpath in files:
        fname = os.path.basename(fpath)
        ok = remove_links_by_url_list(fpath, urls_to_remove)
        log(counter, fname, "xóa liên kết", "thành công" if ok else "không có liên kết khớp")
        if ok:
            success += 1
        counter += 1

    return total, success, total - success


# ====================== MAIN ======================

def get_directory():
    directory = input(messages("directory-prompt", return_string=True)).strip() or "."
    while not os.path.isdir(directory):
        directory = input(messages("directory-invalid", directory, return_string=True)).strip() or "."
    return directory


def get_url_file():
    url_file = input(messages("url-file-prompt", return_string=True)).strip()
    while url_file and not os.path.isfile(url_file):
        url_file = input(messages("url-file-invalid", url_file, return_string=True)).strip()
    return url_file


def main():
    random.seed(datetime.datetime.now().timestamp())

    feature_labels = {
        "1": "date",
        "2": "description",
        "3": "cover + figure cuối trang",
        "4": "figure",
        "5": "thêm tag",
        "6": "lọc & move",
        "7": "xóa liên kết",
    }

    while True:
        try:
            messages("welcome")
            messages("features")
            feature = input(messages("feature-prompt", return_string=True)).strip()

            if not feature or feature == "0":
                sys.exit(0)

            if feature not in feature_labels:
                messages("feature-invalid")
                continue

            directory = get_directory()

            # Thu thập thêm input trước khi xử lý
            extra = {}
            if feature == "6":
                tag_input = input(messages("tag-prompt", return_string=True)).strip()
                if not tag_input:
                    continue
                extra["tag"] = tag_input
                extra["folder"] = input(messages("move-folder-prompt", return_string=True)).strip() or "filtered_by_tag"
            elif feature == "7":
                url_file = get_url_file()
                if not url_file:
                    continue
                extra["url_file"] = url_file

            messages("processing")

            if feature == "1":
                total, success, fail = process_date(directory)
            elif feature == "2":
                total, success, fail = process_description(directory)
            elif feature == "3":
                total, success, fail = process_cover_and_figure(directory)
            elif feature == "4":
                total, success, fail = process_figures(directory)
            elif feature == "5":
                total, success, fail = process_add_tag(directory)
            elif feature == "6":
                total, success, fail = filter_and_move_files(directory, extra["tag"], extra["folder"])
            elif feature == "7":
                total, success, fail = process_remove_links(directory, extra["url_file"])

            messages("complete", total, success, fail)

            next_choice = input(messages("prompt-next", return_string=True)).strip()
            if next_choice == "1":
                webbrowser.open("https://nhavan.vn")
                sys.exit(0)
            elif next_choice == "2":
                sys.exit(0)
            # Mặc định (0 hoặc Enter): vòng lặp tiếp tục

        except (EOFError, KeyboardInterrupt):
            sys.exit(0)


if __name__ == "__main__":
    main()