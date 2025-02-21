import requests
import json
import certifi
from bs4 import BeautifulSoup

# URL of the blog page
URL = "https://uet.vnu.edu.vn/category/sinh-vien/giao-luu-trao-doi-sinh-vien/"

# Your Discord Webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1342442566888591370/55Zpu3WQbXkSbHcC5EHxntq1cLUdQ0Ojryj11EIcJAY5tHiw79aIGsGCXE2bsFE-ytBC"

# File to store last posted article
LAST_POST_FILE = "last_post.txt"


def fetch_latest_articles():
    """Fetch latest articles from the website with SSL verification fixes."""
    try:
        response = requests.get(URL, verify=certifi.where())  # Use certifi for SSL verification
    except requests.exceptions.SSLError:
        print("⚠️ SSL Verification Failed. Retrying without verification...")
        response = requests.get(URL, verify=False)  # Fallback method

    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    for article in soup.select(".blog-item .item-content h3 a"):  # Adjusted selector
        title = article.text.strip()
        link = article["href"]
        articles.append({"title": title, "link": link})

    return articles


def get_last_posted():
    """Read the last posted article from a file."""
    try:
        with open(LAST_POST_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def save_last_posted(title):
    """Save the last posted article title to a file."""
    with open(LAST_POST_FILE, "w", encoding="utf-8") as f:
        f.write(title)


def send_discord_message(article):
    """Send a message to Discord webhook with the newest article."""
    message = {
        "content": f"📢 **New Blog Post Alert!**\n"
                   f"🔗 [{article['title']}]({article['link']})\n"
                   f"<@586892544583925782>"
    }
    headers = {"Content-Type": "application/json"}
    requests.post(WEBHOOK_URL, data=json.dumps(message), headers=headers)


def check_for_updates():
    """Check for new blog posts and send a Discord message if there's an update."""
    latest_articles = fetch_latest_articles()

    if not latest_articles:
        print("No articles found.")
        return

    latest_article = latest_articles[0]  # Get the newest post
    last_posted = get_last_posted()

    if latest_article["title"] != last_posted:
        print(f"New post found: {latest_article['title']}")
        send_discord_message(latest_article)
        save_last_posted(latest_article["title"])
    else:
        print("No new updates.")


# Run the tracker
if __name__ == "__main__":
    check_for_updates()
