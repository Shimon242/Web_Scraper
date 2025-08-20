import requests
from html.parser import HTMLParser
import time

class NodeSeekParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_a = False
        self.in_font = False
        self.current_link = ''
        self.current_text = ''
        self.titles = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href' and '/topic/' in attr[1]:
                    self.in_a = True
                    self.current_link = attr[1]
        if tag == 'font':
            self.in_font = True

    def handle_endtag(self, tag):
        if tag == 'a' and self.in_a:
            self.in_a = False
            self.titles.append(self.current_text.strip())
            self.links.append('https://www.nodeseek.com' + self.current_link)
            self.current_text = ''
        if tag == 'font':
            self.in_font = False

    def handle_data(self, data):
        if self.in_a and self.in_font:
            self.current_text += data

def search_nodeseek(keyword):
    matched_posts = []
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    for page in range(1, 101):  # pages 1 to 100
        url = f"https://www.nodeseek.com/page-{page}"
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"Failed to fetch page {page}, status: {resp.status_code}")
            continue

        parser = NodeSeekParser()
        parser.feed(resp.text)

        # DEBUG: Print out collected titles/links
        for orig_title, link in zip(parser.titles, parser.links):
            print(f"[DEBUG] Title: {orig_title} | Link: {link}")

        # Check for keyword in the original title (case-insensitive)
        for orig_title, link in zip(parser.titles, parser.links):
            if keyword.lower() in orig_title.lower():
                matched_posts.append((orig_title, link))

        time.sleep(1)  # be nice to the server

    return matched_posts

if __name__ == "__main__":
    kw = input("Enter keyword to search in post titles: ").strip()
    results = search_nodeseek(kw)
    print("\n=== Matched Posts ===")
    for title, link in results:
        print(f"{title}\n{link}\n")
