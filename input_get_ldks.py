import requests
from bs4 import BeautifulSoup
import re
import os
# import time
# import random

print("Activate ldks")
OUTPUT_FOLDER = "RawText"
BASE_URL = "http://23.225.121.247"
TARGET_BOOK = str(input("请输入书籍ID: "))
BOOK_INDEX_URL = f"{BASE_URL}/ldks/{TARGET_BOOK}/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "http://23.225.121.247/"
}

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_response(url):
    response = requests.get(url, headers=HEADERS)
    response.encoding = 'utf-8'
    return response

def get_index_dict():
    print("正在获取目录...")
    response = get_response(BOOK_INDEX_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    content_select = soup.find("select", attrs={"name": "pageselect"})

    index_dict = {}
    for option in content_select.find_all("option"):
        value = option.get("value")
        title = option.text.strip()

        if value:
            full_url = BASE_URL + value
            index_dict[title] = full_url

    print("目录获取完成 ✅")
    return index_dict

def get_all_urls(index_dict):
    print("正在获取章节链接...")
    chapter_dict = {}
    for title, url in index_dict.items():
        response = get_response(url)
        # time.sleep(random.uniform(1.0, 2.5))
        soup = BeautifulSoup(response.text, "html.parser")
        content_ul = soup.find_all("ul", attrs={"class": "section-list fix"})

        for link in content_ul[1].find_all("a"):
            href = link.get("href")
            title = link.text.strip()

            if href:
                full_url = BASE_URL + href
                chapter_dict[title] = full_url

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

def extract_and_save(title, html, html2, filename_prefix):
    soup = BeautifulSoup(html, "html.parser")
    soup2 = BeautifulSoup(html2, "html.parser")

    content_div = soup.find("div", id="content")
    content_div2 = soup2.find("div", id="content")

    if not content_div or not content_div2:
        print(f"{title} 未找到正文内容 ❌")
        return False

    lines = get_text(content_div)
    del lines[1]
    del lines[-1]
    new_text = '\n\n'.join(lines)

    lines2 = get_text(content_div2)
    lines2 = lines2[2:]
    new_text2 = '\n\n'.join(lines2)

    final_text = f"{new_text}\n\n{new_text2}"

    filename = f"{filename_prefix}.html"
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    index = 1
    comment_number = re.search(r'\d+', filename).group()

    while os.path.exists(filepath):
        filename = f"{filename_prefix}_{index}.html"
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        comment_number = f"{filename_prefix}_{index}"
        index += 1

    html_content = f"<!-- {comment_number} -->\n<p>{final_text}\n</p>"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
        print(f"{filename} 写入完成 ✅")
    return True

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

def main(start_number=None, end_number=None):
    index_dict = get_index_dict()
    urls = get_all_urls(index_dict)
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
        page2 = url.replace(".html", "_2.html")
        html2 = fetch_chapter_html(page2)

        if html is None:
            with open('error.txt', "a", encoding="utf-8") as f:
                f.write(f"{title} 请求失败\n")
            continue

        extract_and_save(title, html, html2, number)
        FILE_COUNT = max(FILE_COUNT, number)

    print(TITLE_IS_NOT_NUMBER)

    for title in TITLE_IS_NOT_NUMBER:
        url = urls[title]
        html = fetch_chapter_html(url)
        page2 = url.replace(".html", "_2.html")
        html2 = fetch_chapter_html(page2)

        if html is None:
            with open('error2.txt', "a", encoding="utf-8") as f:
                f.write(f"{title} 请求失败\n")
            continue

        FILE_COUNT += 1
        clean_title = re.sub(r'\s+', '', title)
        extract_and_save(title, html, html2, f"{FILE_COUNT}_{clean_title}")

if __name__ == "__main__":
    try:
        START_NUMBER, END_NUMBER = get_number_range()
        main(START_NUMBER, END_NUMBER)
    except ValueError:
        print("❌ something going wrong!")
    pass
pass
