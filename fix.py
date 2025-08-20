import urllib.parse
from html.parser import HTMLParser
import time

# Try cloudscraper first (for Cloudflare), fallback to requests
try:
    import cloudscraper
    scraper = cloudscraper.create_scraper()
except ImportError:
    import requests
    scraper = requests.Session()

# Translation
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
            if "href" in attrs_dict and ("/t/" in attrs_dict["href"] or "/post/" in attrs_dict["href"]):
                self.in_link = True
                self.current_href = attrs_dict["href"]

    def handle_endtag(self, tag):
        if tag == "a" and self.in_link:
            if self.current_href and self.current_text.strip():
                # Capture all text inside <a> including <font>
                self.titles.append(self.current_text.strip())
                self.links.append(urllib.parse.urljoin("https://www.nodeseek.com", self.current_href))
            self.in_link = False
            self.current_href = None
            self.current_text = ""

    def handle_data(self, data):
        if self.in_link:
            # Collect text from any nested tags inside <a>
            self.current_text += data


def search_nodeseek(keyword, max_pages=10):
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
        print(f"\n🔍 Checking {url} ...")

        resp = scraper.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"⚠️ Error on page {page}: status {resp.status_code}")
            continue

        parser = NodeSeekParser()
        parser.feed(resp.text)

        if not parser.titles:
            print("No titles found on this page.")
            continue

        # Translate all titles on this page
        translated_titles = parser.titles
        if translator:
            try:
                translations = translator.translate(parser.titles, dest="en")
                translated_titles = [t.text for t in translations]
            except Exception as e:
                print(f"⚠️ Translation error on page {page}: {e}")

        # Print all translated titles
        print(f"\n--- Page {page} Titles (Translated to English) ---")
        for title in translated_titles:
            print(title)

        # Filter results by keyword
        for title, link in zip(translated_titles, parser.links):
            if keyword.lower() in title.lower():
                all_results.append({"title": title, "url": link})

        time.sleep(1)  # avoid hammering the server

    return all_results


if __name__ == "__main__":
    keyword = input("Enter search keyword: ").strip()
    matches = search_nodeseek(keyword, max_pages=10)

    if not matches:
        print("\nNo matching posts found in 10 pages.")
    else:
        print(f"\n✅ Found {len(matches)} matching posts (titles translated to English):")
        for item in matches:
            print(f"- {item['title']}: {item['url']}")
