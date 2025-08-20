import urllib.parse
from html.parser import HTMLParser
import time

try:
    import cloudscraper
    scraper = cloudscraper.create_scraper()
except ImportError:
    import requests
    scraper = requests.Session()

try:
    from googletrans import Translator
    translator = Translator()
except ImportError:
    translator = None


class NodeSeekParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_link = False
        self.current_href = None
        self.current_text = ""
        self.titles = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs_dict = dict(attrs)
            if "href" in attrs_dict and "/topic/" in attrs_dict["href"]:
                self.in_link = True
                self.current_href = attrs_dict["href"]

    def handle_endtag(self, tag):
        if tag == "a" and self.in_link:
            if self.current_href and self.current_text.strip():
                self.titles.append(self.current_text.strip())
                self.links.append(
                    urllib.parse.urljoin("https://www.nodeseek.com", self.current_href)
                )
            self.in_link = False
            self.current_href = None
            self.current_text = ""

    def handle_data(self, data):
        if self.in_link:
            self.current_text += data


def search_nodeseek(keyword, max_pages=100):
    all_results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.nodeseek.com/"
    }

    for page in range(1, max_pages + 1):
        url = f"https://www.nodeseek.com/page-{page}"
        print(f"🔍 Checking {url} ...")

        resp = scraper.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"⚠️ Error on page {page}: status {resp.status_code}")
            continue

        parser = NodeSeekParser()
        parser.feed(resp.text)

        # DEBUG: Print out collected titles/links
        for orig_title, link in zip(parser.titles, parser.links):
            print(f"[DEBUG] Title: {orig_title} | Link: {link}")

        for orig_title, link in zip(parser.titles, parser.links):
            matched = False
            if keyword.lower() in orig_title.lower():
                matched = True
            else:
                if translator:
                    try:
                        trans = translator.translate(orig_title, dest="en").text
                        if keyword.lower() in trans.lower():
                            orig_title = trans
                            matched = True
                        else:
                            continue
                    except Exception:
                        continue

            if matched:
                all_results.append({"title": orig_title, "url": link})

        time.sleep(1)

    return all_results


if __name__ == "__main__":
    keyword = input("Enter search keyword: ").strip()
    matches = search_nodeseek(keyword, max_pages=100)

    if not matches:
        print("No matching posts found in 100 pages.")
    else:
        print(f"\n Found {len(matches)} matching posts:")
        for item in matches:
            print(f"- {item['title']}: {item['url']}")
