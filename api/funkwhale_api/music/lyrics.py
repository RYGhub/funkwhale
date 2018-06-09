import urllib.request
from bs4 import BeautifulSoup


def _get_html(url):
    with urllib.request.urlopen(url) as response:
        html = response.read()
    return html.decode("utf-8")


def extract_content(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.find_all("div", class_="lyricbox")[0].contents


def clean_content(contents):
    final_content = ""
    for e in contents:
        if e == "\n":
            continue
        if e.name == "script":
            continue
        if e.name == "br":
            final_content += "\n"
            continue
        try:
            final_content += e.text
        except AttributeError:
            final_content += str(e)
    return final_content
