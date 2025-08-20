from html.parser import HTMLParser
import urllib.parse
import time
import requests

# Use cloudscraper if available, otherwise fallback to requests
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
        self.in_post_title_div = False
        self.in_a = False
        self.current_text = ""
        self.current_link = ""
        self.titles = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "div" and attrs_dict.get("class") == "post-title":
            self.in_post_title_div = True
        if self.in_post_title_div and tag == "a" and "href" in attrs_dict:
            self.in_a = True
            self.current_link = attrs_dict["href"]

    def handle_endtag(self, tag):
        if tag == "a" and self.in_a:
            self.in_a = False
        if tag == "div" and self.in_post_title_div:
            if self.current_text.strip():
                self.titles.append(self.current_text.strip())
                self.links.append(urllib.parse.urljoin("https://www.nodeseek.com", self.current_link))
            self.current_text = ""
            self.current_link = ""
            self.in_post_title_div = False

    def handle_data(self, data):
        if self.in_post_title_div and self.in_a:
            self.current_text += data


def search_nodeseek(keyword, max_pages=100):
    results = []

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
            print(f"⚠️ Error fetching page {page}: {resp.status_code}")
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
                print(f" Finished scanning this page {page}")

        # Print all titles for this page
        #print(f"\n--- Page {page} Titles ---")
        #for t in translated_titles:
        #    print(t)

        # Filter by keyword
        for title, link in zip(translated_titles, parser.links):
            if keyword.lower() in title.lower():
                results.append({"title": title, "url": link})

        time.sleep(1.5)  # polite delay

    return results


if __name__ == "__main__":
    keyword = input("Enter search keyword: ").strip()
    matches = search_nodeseek(keyword, max_pages=100)
    MESSAGE = []

    if not matches:
        print("\nNo matching posts found in 30 pages.")
    else:
        print(f"\n✅ Found {len(matches)} matching posts:")
        for item in matches:
            line = f"- {item['title']}: {item['url']}"
            print(line)
            MESSAGE.append(line)
          
TOKEN = ":AAHxFno48Um2htiDmWvFjijJWWYdx10DfE0"
CHAT_ID = "-1002573467611"  # your group chat ID

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": MESSAGE
}

resp = requests.post(url, data=payload)

if resp.status_code == 200:
    print("✅ Message sent successfully!")
else:
    print("❌ Failed to send message:", resp.text)
