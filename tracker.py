import requests
from bs4 import BeautifulSoup
import json

# Website URL to monitor
URL = "https://uet.vnu.edu.vn/category/sinh-vien/giao-luu-trao-doi-sinh-vien/"
WEBHOOK_URL = "https://discord.com/api/webhooks/1342442566888591370/55Zpu3WQbXkSbHcC5EHxntq1cLUdQ0Ojryj11EIcJAY5tHiw79aIGsGCXE2bsFE-ytBC"  # Replace with your actual webhook

# File to store previously seen articles
DATA_FILE = "tracked_data.json"

def fetch_latest_articles():
    """Scrapes the latest articles from the website."""
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    
    articles = []
    for article in soup.select(".td_module_10 .td-module-title a"):  # Adjust selector if needed
        title = article.text.strip()
        link = article["href"]
        articles.append({"title": title, "link": link})

    return articles

def load_previous_articles():
    """Loads previously saved articles from a file."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_articles(articles):
    """Saves articles to a file."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(articles, file, indent=2)

def send_discord_notification(new_articles):
    """Sends new articles to Discord."""
    for article in new_articles:
        message = f"🆕 **New Article Posted!**\n🔗 [{article['title']}]({article['link']})"
        payload = {"content": message}
        requests.post(WEBHOOK_URL, json=payload)

def check_for_updates():
    """Checks if new articles have been posted."""
    latest_articles = fetch_latest_articles()
    previous_articles = load_previous_articles()

    # Find new articles
    new_articles = [article for article in latest_articles if article not in previous_articles]

    if new_articles:
        print("New articles found! Sending to Discord...")
        send_discord_notification(new_articles)
        save_articles(latest_articles)
    else:
        print("No new articles found.")

if __name__ == "__main__":
    check_for_updates()
