import os
import requests
import certifi
from bs4 import BeautifulSoup

URL = "https://uet.vnu.edu.vn/category/sinh-vien/giao-luu-trao-doi-sinh-vien/"
WEBHOOK_URL = "https://discord.com/api/webhooks/1342442566888591370/55Zpu3WQbXkSbHcC5EHxntq1cLUdQ0Ojryj11EIcJAY5tHiw79aIGsGCXE2bsFE-ytBC"

def fetch_latest_articles():
    """Fetch latest articles from the website with SSL verification fixes."""
    try:
        response = requests.get(URL, verify=certifi.where())  # Use certifi for SSL verification
    except requests.exceptions.SSLError:
        print("⚠️ SSL Verification Failed. Retrying without verification...")
        response = requests.get(URL, verify=False)  # Fallback method

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract first blog post (newest)
    article = soup.select_one(".blog-item .item-content h3 a")
    
    if article:
        title = article.text.strip()
        link = article["href"]
        return {"title": title, "link": link}
    return None

def read_last_post():
    """Read last saved post URL from GitHub Secret (via environment variable)."""
    return os.getenv("LAST_POST_URL", "")

def save_last_post(url):
    """Save last post URL to last_post.txt (so GitHub Actions can update the Secret)."""
    with open("last_post.txt", "w", encoding="utf-8") as file:
        file.write(url)

def send_discord_notification(article):
    """Send a notification to Discord webhook."""
    message = {
        "content": f"<@586892544583925782> 🆕 **New Blog Post:** {article['title']}\n🔗 {article['link']}"
    }
    requests.post(WEBHOOK_URL, json=message)

def check_for_updates():
    """Check for new articles and send notification if updated."""
    latest_article = fetch_latest_articles()
    if not latest_article:
        print("❌ No new articles found.")
        return

    last_post_url = read_last_post()

    if latest_article["link"] != last_post_url:
        print(f"✅ New post found: {latest_article['title']}")
        send_discord_notification(latest_article)
        save_last_post(latest_article["link"])  # Save to last_post.txt for GitHub Actions
    else:
        print("🔄 No new updates.")

if __name__ == "__main__":
    check_for_updates()
