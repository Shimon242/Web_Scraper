import requests
from bs4 import BeautifulSoup
import urllib.parse

def search_nodeseek(keyword):
    # Update this to the actual search endpoint on nodeseek
    base_url = "https://www.nodeseek.com/search"
    params = {"q": keyword}
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; YourScraper/1.0)"
    }

    resp = requests.get(base_url, params=params, headers=headers)
    if resp.status_code != 200:
        print(f"Error: Received status code {resp.status_code}")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')

    results = []
    # Modify selector based on the page structure for post links
    for link in soup.select("a.post-link"):
        title = link.get_text(strip=True)
        href = link.get("href")
        full_url = urllib.parse.urljoin(base_url, href)
        results.append({"title": title, "url": full_url})

    return results

if __name__ == "__main__":
    keyword = input("Enter search keyword for NodeSeek: ").strip()
    matches = search_nodeseek(keyword)
    if not matches:
        print("No matching posts found.")
    else:
        print("\nFound matches:")
        for item in matches:
            print(f"- {item['title']}: {item['url']}")
