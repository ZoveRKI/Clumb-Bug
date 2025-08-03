import requests
from bs4 import BeautifulSoup
import os

url = "https://www.drxsw.com/book/3509660/1963833788.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
}

response = requests.get(url, headers=headers)
response.encoding = 'utf-8'  # 明确编码，避免乱码

# # 打印不出正文，但保存的HTML文件是全的
# print(response.text)
# with open("test.html", "w", encoding="utf-8") as f:
#     f.write(response.text)

output_dir = "RawText"
html_raw_text = response.text
soup = BeautifulSoup(html_raw_text, "html.parser")
content_div = soup.find("div", id="TextContent")

os.makedirs(output_dir, exist_ok=True)

# 去掉多余空白和&nbsp;之类的字符
if content_div:
    i = 413
    filename = f"{i}.html"
    filepath = os.path.join(output_dir, filename)
    title = soup.find("div", id="mlfy_main_text").find("h1").get_text(strip=True)
    text = content_div.get_text(separator='\n\n', strip=True)
    html_content = f"<!-- {i} -->\n<p>{title}\n\n{text}\n</p>"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
else:
    i = 413
    print(f"{i}未找到正文内容")
