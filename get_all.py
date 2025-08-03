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
TITLE_IS_NOT_NUMBER = []

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

def main():
    urls = get_all_urls()

    # test = [
    #     '第283章 前世今生，七情劫之色之一劫',
    #     '第284章 再遇，他秦长生，绝不会趁人之危',
    #     '第284章 我是被迫的！第二劫，傲慢',
    #     '番外 秦长生师徒的日常',
    #     '第285章 第三劫，暴怒，时间长河的尽头',
    # ]

    for url in urls:
    # for url in test:
        if not re.search(r'\d+', url):
            TITLE_IS_NOT_NUMBER.append(url)
            continue

        try:
            chapter = requests.get(urls[url], headers=HEADERS)
            chapter.encoding = 'utf-8'
            time.sleep(random.uniform(1.0, 2.5))
        except Exception as e:
            with open('error.text', "w", encoding="utf-8") as f:
                f.write(f"{url} 请求失败：{e}")
            continue

        chapter_soup = BeautifulSoup(chapter.text, "html.parser")
        content_div = chapter_soup.find("div", id="TextContent")

        if content_div:
            title = chapter_soup.find("div", id="mlfy_main_text").find("h1").get_text(strip=True)
            match = re.search(r'\d+', title)

            filename = f"{match.group()}.html"
            filepath = os.path.join(OUTPUT_FOLDER, filename)
            if os.path.exists(filepath):
                index = 1
                while os.path.exists(filepath):
                    filename = f"{match.group()}_{index}.html"
                    filepath = os.path.join(OUTPUT_FOLDER, filename)
                    index += 1

            text = content_div.get_text(separator='\n\n', strip=True)
            html_content = f"<!-- {match.group()} -->\n<p>{title}\n\n{text}\n</p>"

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
                print(f"{filename} 写入完成 ✅")
                FILE_COUNT = int(match.group())
        else:
            print(f"{url} 未找到正文内容 ❌")
    pass

    print(TITLE_IS_NOT_NUMBER)

    if TITLE_IS_NOT_NUMBER:
        for title_is_not_number in TITLE_IS_NOT_NUMBER:
            try:
                chapter = requests.get(urls[title_is_not_number], headers=HEADERS)
                chapter.encoding = 'utf-8'
                time.sleep(random.uniform(1.0, 2.5))
            except Exception as e:
                with open('error2.text', "w", encoding="utf-8") as f:
                    f.write(f"{title_is_not_number} 请求失败：{e}")
                continue

            chapter_soup = BeautifulSoup(chapter.text, "html.parser")
            content_div = chapter_soup.find("div", id="TextContent")

            if content_div:
                title = chapter_soup.find("div", id="mlfy_main_text").find("h1").get_text(strip=True)
                FILE_COUNT += 1

                filename = f"{FILE_COUNT}_{re.sub(r'\s+', '', title)}.html"
                filepath = os.path.join(OUTPUT_FOLDER, filename)

                text = content_div.get_text(separator='\n\n', strip=True)
                html_content = f"<!-- {FILE_COUNT} -->\n<p>{title}\n\n{text}\n</p>"

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(html_content)
                    print(f"{filename} 写入完成 ✅")
            else:
                print(f"{url} 未找到正文内容 ❌")
        pass
pass

if __name__ == "__main__":
    main()
