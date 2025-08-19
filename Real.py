import requests
from html.parser import HTMLParser
import urllib.parse

class NodeSeekParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_link = False
        self.current_href = None
        self.results = []
        self.current_text = ""

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs_dict = dict(attrs)
            # Adjust this condition to match NodeSeek's actual link structure
            if "href" in attrs_dict and "post" in attrs_dict["href"]:
                self.in_link = True
                self.current_href = attrs_dict["href"]

    def handle_endtag(self, tag):
        if tag == "a" and self.in_link:
            if self.current_href and self.current_text.strip():
                self.results.append({
                    "title": self.current_text.strip(),
                    "url": urllib.parse.urljoin("https://www.nodeseek.com", self.current_href)
                })
            self.in_link = False
            self.current_href = None
            self.current_text = ""

    def handle_data(self, data):
        if self.in_link:
            self.current_text += data

def search_nodeseek(keyword):
    base_url = "https://www.nodeseek.com/search"
    params = {"q": keyword}
    
    # More realistic headers to avoid 403
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.nodeseek.com/"
    }

    resp = requests.get(base_url, params=params, headers=headers)
    if resp.status_code != 200:
        print(f"Error: Received status code {resp.status_code}")
        return []

    parser = NodeSeekParser()
    parser.feed(resp.text)
    return parser.results

if __name__ == "__main__":
    keyword = input("Enter search keyword for NodeSeek: ").strip()
    matches = search_nodeseek(keyword)
    if not matches:
        print("No matching posts found.")
    else:
        print("\nFound matches:")
        for item in matches:
            print(f"- {item['title']}: {item['url']}")
