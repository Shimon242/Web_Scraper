from html.parser import HTMLParser
import urllib.parse
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


class PostTitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_post_div = False
        self.in_font = False
        self.current_text = ""
        self.titles = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "div" and attrs_dict.get("class") == "post-list-content":
            self.in_post_div = True
        if self.in_post_div and tag == "font":
            self.in_font = True

    def handle_endtag(self, tag):
        if tag == "font" and self.in_font:
            self.in_font = False
            if self.current_text.strip():
                self.titles.append(self.current_text.strip())
            self.current_text = ""
        if tag == "div" and self.in_post_div:
            self.in_post_div = False

    def handle_data(self, data):
        if self.in_post_div and self.in_font:
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

        parser = PostTitleParser()
        parser.feed(resp.text)

        if not parser.titles:
            print("No titles found on this page.")
            continue

        # Translate titles if translator is available
        translated_titles = parser.titles
        if translator:
            try:
                translations = translator.translate(parser.titles, dest="en")
                translated_titles = [t.text for t in translations]
            except Exception as e:
                print(f"⚠️ Translation error on page {page}: {e}")

        # Print all titles
        print(f"\n--- Page {page} Titles (Translated to English) ---")
        for t in translated_titles:
            print(t)

        # Filter by keyword
        for title in translated_titles:
            if keyword.lower() in title.lower():
                all_results.append(title)

        time.sleep(1)

    return all_results


if __name__ == "__main__":
    keyword = input("Enter search keyword: ").strip()
    matches = search_nodeseek(keyword, max_pages=10)

    if not matches:
        print("\nNo matching posts found in 10 pages.")
    else:
        print(f"\n✅ Found {len(matches)} matching posts (titles translated to English):")
        for title in matches:
            print(f"- {title}")
