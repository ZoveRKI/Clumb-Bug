import requests
from bs4 import BeautifulSoup
import re
import os
import time
import random

OUTPUT_FOLDER = "RawText"
BASE_URL = "https://www.drxsw.com"
TARGET_BOOK = "3509660"
BOOK_INDEX_URL = f"https://www.drxsw.com/book/{TARGET_BOOK}/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.drxsw.com/"
}

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_all_urls():
    response = requests.get(BOOK_INDEX_URL, headers=HEADERS)
    response.encoding = 'utf-8'
    list_soup = BeautifulSoup(response.text, "html.parser")
    content_ul = list_soup.find("ul", id="chapterList")

    chapter_dict = {}
    for link in content_ul.find_all("a"):
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

def extract_and_save(title, html, filename_prefix):
    soup = BeautifulSoup(html, "html.parser")
    content_div = soup.find("div", id="TextContent")

    if not content_div:
        print(f"{title} 未找到正文内容 ❌")
        return False

    title_tag = soup.find("div", id="mlfy_main_text").find("h1")
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

def main():
    urls = get_all_urls()
    TITLE_IS_NOT_NUMBER = []
    FILE_COUNT = 0

    # test = {
    #     '第283章 前世今生，七情劫之色之一劫': f'{BASE_URL}/book/3509660/1925636303.html',
    #     '第284章 再遇，他秦长生，绝不会趁人之危': f'{BASE_URL}/book/3509660/1925636366.html',
    #     '第284章 我是被迫的！第二劫，傲慢': f'{BASE_URL}/book/3509660/1927218791.html',
    #     '番外 秦长生师徒的日常': f'{BASE_URL}/book/3509660/2053481357.html',
    #     '第285章 第三劫，暴怒，时间长河的尽头': f'{BASE_URL}/book/3509660/1927418402.html',
    # }

    # for title, url in test.items():
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
    main()
