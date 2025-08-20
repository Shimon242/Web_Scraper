import urllib.parse
from html.parser import HTMLParser

# Try cloudscraper first (for Cloudflare), fallback to requests
try:
    import cloudscraper
    scraper = cloudscraper.create_scraper()
except ImportError:
    import requests
    scraper = requests.Session()

# Optional: translation support
try:
    from googletrans import Translator
    translator = Translator()
except ImportError:
    translator = None

class NodeSeekParser(HTMLParser):
    def __init__(self, keyword):
        super().__init__()
        self.keyword = keyword.lower()
        self.in_link = False
        self.current_href = None
        self.results = []
        self.current_text = ""

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs_dict = dict(attrs)
            # Adjust this if NodeSeek uses different URL structure for posts
            if "href" in attrs_dict and "post" in attrs_dict["href"]:
                self.in_link = True
                self.current_href = attrs_dict["href"]

    def handle_endtag(self, tag):
        if tag == "a" and self.in_link:
            if self.current_href and self.current_text.strip():
                title = self.current_text.strip()

                # Translate to English (optional)
                if translator:
                    try:
                        title = translator.translate(title, dest="en").text
                    except Exception:
                        pass

                # ✅ Only keep results that contain the keyword in the title
                if self.keyword in title.lower():
                    self.results.append({
                        "title": title,
                        "url": urllib.parse.urljoin("https://www.nodeseek.com", self.current_href)
                    })

            self.in_link = False
            self.current_href = None
            self.current_text = ""

    def handle_data(self, data):
        if self.in_link:
            self.current_text += data

def search_nodeseek(keyword):
    base_url = "https://www.nodeseek.com"
    params = {"q": keyword}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.nodeseek.com/"
    }

    resp = scraper.get(base_url, params=params, headers=headers)
    if resp.status_code != 200:
        print(f"Error: Received status code {resp.status_code}")
        return []

    parser = NodeSeekParser(keyword)
    parser.feed(resp.text)
    return parser.results

if __name__ == "__main__":
    keyword = input("Enter search keyword for NodeSeek: ").strip()
    matches = search_nodeseek(keyword)
    if not matches:
        print("No matching posts found in titles.")
    else:
        print("\nFound matching posts (titles contain keyword):")
        for item in matches:
            print(f"- {item['title']}: {item['url']}")
