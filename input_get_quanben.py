import requests
from bs4 import BeautifulSoup
import re
import os
# import time
# import random

print("Activate ldks")
OUTPUT_FOLDER = "RawText"
BASE_URL = "https://www.quanben.io"
TARGET_BOOK = str(input("请输入书籍名: "))
TOTAL_CHAPTERS = int(input("请输入总章节数: "))
BOOK_INDEX_URL = f"{BASE_URL}/n/{TARGET_BOOK}/list.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.quanben.io/"
}

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_response(url):
    response = requests.get(url, headers=HEADERS)
    response.encoding = 'utf-8'
    return response

def get_all_urls():
    print("正在获取章节链接...")

    chapter_dict = {}
    for num in range(TOTAL_CHAPTERS):
        link = f"{BASE_URL}/n/{TARGET_BOOK}/{num+1}.html"

        chapter_dict[str(num+1)] = link

    print("所有章节链接获取完成 ✅")
    return chapter_dict

def fetch_chapter_html(url):
    try:
        response = get_response(url)
        # time.sleep(random.uniform(1.0, 2.5))
        return response.text
    except Exception as e:
        return None, str(e)

def get_text(content_div):
    text = content_div.get_text(separator='\n\n', strip=True)
    lines = text.split('\n\n')
    return lines

def extract_and_save(title, html, filename_prefix):
    soup = BeautifulSoup(html, "html.parser")
    content_div = soup.find("div", class_="main")

    if not content_div:
        print(f"{title} 未找到正文内容 ❌")
        return False

    title_tag = content_div.find("h1")
    real_title = title_tag.get_text(strip=True) if title_tag else title

    text = content_div.find("div", id="content").get_text(separator='\n\n', strip=True)

    filename = f"{filename_prefix}.html"
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    index = 1
    comment_number = re.search(r'\d+', filename).group()

    while os.path.exists(filepath):
        filename = f"{filename_prefix}_{index}.html"
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        comment_number = f"{filename_prefix}_{index}"
        index += 1

    html_content = f"<!-- {comment_number} -->\n<p>{real_title}\n\n{text}\n</p>"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
        print(f"{filename} 写入完成 ✅")
    return True

def get_numbering_options():
    mode_input = input(
        "请输入编号规则（留空使用标题数字，输入任意内容使用纯数字顺序编号）: "
    ).strip()

    if not mode_input:
        return False, None

    while True:
        start_input = input("请输入顺序编号起始值（0 或 1）: ").strip()
        if start_input in {"0", "1"}:
            return True, int(start_input)

        print("❌ 顺序编号起始值只能是 0 或 1，请重新输入。")

def get_number_range():
    while True:
        start_input = input("请输入起始编号（留空则不限制）: ").strip()
        end_input = input("请输入结束编号（留空则不限制）: ").strip()

        try:
            start_number = int(start_input) if start_input else None
            end_number = int(end_input) if end_input else None
        except ValueError:
            print("❌ 编号必须是正整数，请重新输入。")
            continue

        if start_number is not None and start_number <= 0:
            print("❌ 起始编号必须大于 0，请重新输入。")
            continue

        if end_number is not None and end_number <= 0:
            print("❌ 结束编号必须大于 0，请重新输入。")
            continue

        if (
            start_number is not None
            and end_number is not None
            and start_number > end_number
        ):
            print("❌ 起始编号不能大于结束编号，请重新输入。")
            continue

        return start_number, end_number

def main(
    start_number=None,
    end_number=None,
    use_sequential_numbering=False,
    sequential_start=None,
):
    urls = get_all_urls()

    if use_sequential_numbering:
        if sequential_start not in (0, 1):
            raise ValueError("顺序编号起始值只能是 0 或 1")

        current_number = sequential_start
        for title, url in urls.items():
            html = fetch_chapter_html(url)

            if html is None:
                with open('error.txt', "a", encoding="utf-8") as f:
                    f.write(f"{title} 请求失败\n")
                continue

            if extract_and_save(title, html, current_number):
                current_number += 1

        return

    TITLE_IS_NOT_NUMBER = []
    FILE_COUNT = 0
    has_number_range = start_number is not None or end_number is not None

    for title, url in urls.items():
        match = re.search(r'\d+', title)
        if not match:
            if not has_number_range:
                TITLE_IS_NOT_NUMBER.append(title)
            continue

        number = int(match.group())
        if start_number is not None and number < start_number:
            continue
        if end_number is not None and number > end_number:
            continue

        html = fetch_chapter_html(url)

        if html is None:
            with open('error.txt', "a", encoding="utf-8") as f:
                f.write(f"{title} 请求失败\n")
            continue

        extract_and_save(title, html, number)
        FILE_COUNT = max(FILE_COUNT, number)

    print(TITLE_IS_NOT_NUMBER)

    for title in TITLE_IS_NOT_NUMBER:
        url = urls[title]
        html = fetch_chapter_html(url)

        if html is None:
            with open('error2.txt', "a", encoding="utf-8") as f:
                f.write(f"{title} 请求失败\n")
            continue

        FILE_COUNT += 1
        clean_title = re.sub(r'\s+', '', title)
        extract_and_save(title, html, f"{FILE_COUNT}_{clean_title}")

if __name__ == "__main__":
    try:
        USE_SEQUENTIAL_NUMBERING, SEQUENTIAL_START = get_numbering_options()
        if USE_SEQUENTIAL_NUMBERING:
            main(
                use_sequential_numbering=True,
                sequential_start=SEQUENTIAL_START,
            )
        else:
            START_NUMBER, END_NUMBER = get_number_range()
            main(START_NUMBER, END_NUMBER)
    except ValueError:
        print("❌ something going wrong!")
    pass
pass
