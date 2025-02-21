import requests
import certifi
from bs4 import BeautifulSoup
import json

# Website URL and Discord Webhook
URL = "https://uet.vnu.edu.vn/category/sinh-vien/giao-luu-trao-doi-sinh-vien/"
WEBHOOK_URL = "https://discord.com/api/webhooks/1342442566888591370/55Zpu3WQbXkSbHcC5EHxntq1cLUdQ0Ojryj11EIcJAY5tHiw79aIGsGCXE2bsFE-ytBC"  # Replace with your webhook
DATA_FILE = "tracked_data.json"

def fetch_latest_articles():
    """Fetch latest articles from the website with SSL verification fixes."""
    try:
        response = requests.get(URL, verify=certifi.where())  # Use certifi for SSL verification
    except requests.exceptions.SSLError:
        print("⚠️ SSL Verification Failed. Retrying without verification...")
        response = requests.get(URL, verify=False)  # Fallback method

    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    for article in soup.select(".td_module_10 .td-module-title a"):
        title = article.text.strip()
        link = article["href"]
        articles.append({"title": title, "link": link})

    return articles

def load_previous_articles():
    """Load previous articles from a file."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_articles(articles):
    """Save articles to a file."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(articles, file, indent=2)

def send_discord_notification(new_articles):
    """Send updates to Discord with mention if new articles are found."""
    if new_articles:
        mention = "<@586892544583925782>"  # Pings the user when there's an update
        for article in new_articles:
            message = f"{mention} 🆕 **New Article Posted!**\n🔗 [{article['title']}]({article['link']})"
            payload = {"content": message}
            requests.post(WEBHOOK_URL, json=payload)
    else:
        # Sends a message every time it checks (without pinging)
        payload = {"content": "✅ Website check complete. No new articles found."}
        requests.post(WEBHOOK_URL, json=payload)

def check_for_updates():
    """Check for new updates and send Discord messages."""
    latest_articles = fetch_latest_articles()
    previous_articles = load_previous_articles()

    # Find new articles
    new_articles = [article for article in latest_articles if article not in previous_articles]

    # Send notifications & update data
    send_discord_notification(new_articles)
    save_articles(latest_articles)

if __name__ == "__main__":
    check_for_updates()
