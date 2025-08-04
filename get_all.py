import requests
from bs4 import BeautifulSoup
import re
import os
import time
import random

OUTPUT_FOLDER = "RawText"
BASE_URL = str(input("请输入网站基础URL(https://www.example.com): ")).strip()
TARGET_BOOK = str(input("请输入书籍ID: "))
INDEX_URL = str(input("请输入书籍索引URL: "))
BOOK_INDEX_URL = f"{INDEX_URL}/{TARGET_BOOK}/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": BASE_URL
}

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_all_urls(chapter_list_element, chapter_list_type, chapter_list_value, link_element):
    response = requests.get(BOOK_INDEX_URL, headers=HEADERS)
    response.encoding = 'utf-8'
    list_soup = BeautifulSoup(response.text, "html.parser")
    content_ul = list_soup.find(chapter_list_element, **{chapter_list_type: chapter_list_value})

    chapter_dict = {}
    for link in content_ul.find_all(link_element):
        href = link.get("href")
        title = link.text.strip()

        if href:
            full_url = BASE_URL + href
            chapter_dict[title] = full_url

    return chapter_dict

def fetch_chapter_html(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.encoding = 'utf-8'
        time.sleep(random.uniform(1.0, 2.5))
        return response.text
    except Exception as e:
        return None, str(e)
pass

def extract_and_save(title, html, filename_prefix, text_element, text_type, text_value, title_element, title_type, title_value):
    soup = BeautifulSoup(html, "html.parser")
    content_div = soup.find(text_element, **{text_type: text_value})

    if not content_div:
        print(f"{title} 未找到正文内容 ❌")
        return False

    title_tag = soup.find(title_element, **{title_type: title_value}).find("h1")
    real_title = title_tag.get_text(strip=True) if title_tag else title

    text = content_div.get_text(separator='\n\n', strip=True)

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

def main(chapter_list_element, chapter_list_type, chapter_list_value, link_element, text_element, text_type, text_value, title_element, title_type, title_value):
    urls = get_all_urls(chapter_list_element, chapter_list_type, chapter_list_value, link_element)
    TITLE_IS_NOT_NUMBER = []
    FILE_COUNT = 0

    for title, url in urls.items():
        match = re.search(r'\d+', title)
        if not match:
            TITLE_IS_NOT_NUMBER.append(title)
            continue

        number = int(match.group())
        html = fetch_chapter_html(url)

        if html is None:
            with open('error.txt', "a", encoding="utf-8") as f:
                f.write(f"{title} 请求失败\n")
            continue

        extract_and_save(title, html, number, text_element, text_type, text_value, title_element, title_type, title_value)
        FILE_COUNT = max(FILE_COUNT, number)
        pass

    print(TITLE_IS_NOT_NUMBER)

    for title_is_not_number in TITLE_IS_NOT_NUMBER:
        url = urls[title_is_not_number]
        html = fetch_chapter_html(url)
        if html is None:
            with open('error2.txt', "a", encoding="utf-8") as f:
                f.write(f"{title_is_not_number} 请求失败\n")
            continue

        FILE_COUNT += 1
        clean_title = re.sub(r'\s+', '', title_is_not_number)
        extract_and_save(title, html, f"{FILE_COUNT}_{clean_title}")
        pass
    pass
pass


if __name__ == "__main__":
    try:
        chapter_list_element = str(input("请输入目录所在HTML标签（如ul或div）: ")).strip()
        chapter_list_type = str(input("请输入目录所在HTML标签类型（如id或class_）: ")).strip()    # class关键字冲突，所以需要加下划线
        chapter_list_value = str(input("请输入目录所在HTML标签的名称（如chapterList）: ")).strip()

        link_element = str(input("请输入链接所在HTML标签（如a）: ")).strip()

        text_element = str(input("请输入正文所在HTML标签（如div）: ")).strip()
        text_type = str(input("请输入正文所在HTML标签类型（如id或class_）: ")).strip()
        text_value = str(input("请输入正文所在HTML标签的名称（如TextContent）: ")).strip()

        title_element = str(input("请输入标题所在HTML标签（如div）: ")).strip()
        title_type = str(input("请输入标题所在HTML标签类型（如id或class_）: ")).strip()
        title_value = str(input("请输入标题所在HTML标签的名称（如TitleContent）: ")).strip()

        main(chapter_list_element, chapter_list_type, chapter_list_value, link_element, text_element, text_type, text_value, title_element, title_type, title_value)
    except ValueError:
        print("❌ something going wrong!")
    pass
pass
