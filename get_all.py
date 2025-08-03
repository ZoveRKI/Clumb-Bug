import requests
from bs4 import BeautifulSoup
import re
import os

OUTPUT_FOLDER = "RawText"
BASE_URL = "https://www.drxsw.com"
TARGET_BOOK = "3509660"
BOOK_INDEX_URL = f"https://www.drxsw.com/book/{TARGET_BOOK}/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.drxsw.com/"
}

response = requests.get(BOOK_INDEX_URL, headers=HEADERS)
response.encoding = 'utf-8'
list_soup = BeautifulSoup(response.text, "html.parser")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_all_urls():
    content_ul = list_soup.find("ul", id="chapterList")
    chapter_dict = {}

    for link in content_ul.find_all("a"):
        href = link.get("href")
        title = link.text.strip()
        match = re.search(r'\d+', title)

        if match and href:
            number = int(match.group())
            full_url = BASE_URL + href
            chapter_dict[number] = full_url

    return chapter_dict

def main():
    urls = get_all_urls()

    for url in urls:
        chapter = requests.get(urls[url], headers=HEADERS)
        chapter.encoding = 'utf-8'
        chapter_soup = BeautifulSoup(chapter.text, "html.parser")
        content_div = chapter_soup.find("div", id="TextContent")

        if content_div:
            title = chapter_soup.find("div", id="mlfy_main_text").find("h1").get_text(strip=True)
            filename = f"{url}.html"
            filepath = os.path.join(OUTPUT_FOLDER, filename)
            text = content_div.get_text(separator='\n\n', strip=True)
            html_content = f"<!-- {url} -->\n<p>{title}\n\n{text}\n</p>"

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)

            print(f"{filename} 写入完成 ✅")
        else:
            print(f"{url} 未找到正文内容 ❌")
    pass
pass

if __name__ == "__main__":
    main()
