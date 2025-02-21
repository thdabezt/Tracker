import os
import requests
import certifi
from bs4 import BeautifulSoup

URL = "https://uet.vnu.edu.vn/category/sinh-vien/giao-luu-trao-doi-sinh-vien/"
WEBHOOK_URL = "https://discord.com/api/webhooks/1342442566888591370/55Zpu3WQbXkSbHcC5EHxntq1cLUdQ0Ojryj11EIcJAY5tHiw79aIGsGCXE2bsFE-ytBC"
LAST_POST_FILE = "last_post.txt"

def fetch_latest_article():
    """Fetch the latest article from the website with SSL verification."""
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
    
    print("❌ No articles found on the website.")
    return None

def read_last_post():
    """Read last saved post URL from last_post.txt."""
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r", encoding="utf-8") as file:
            return file.read().strip()
    
    print("🔍 last_post.txt not found. Assuming first run.")
    return None

def save_last_post(url):
    """Save last post URL to last_post.txt."""
    with open(LAST_POST_FILE, "w", encoding="utf-8") as file:
        file.write(url)

def send_discord_notification(article):
    """Send a notification to Discord webhook."""
    message = {
        "content": f"<@586892544583925782> 🆕 **New Blog Post:** {article['title']}\n🔗 {article['link']}"
    }
    response = requests.post(WEBHOOK_URL, json=message)
    if response.status_code == 204:
        print("✅ Discord notification sent successfully.")
    else:
        print(f"⚠️ Failed to send Discord notification. Status: {response.status_code}, Response: {response.text}")

def check_for_updates():
    """Check for new articles and send notification if updated."""
    print("🔄 Checking for new blog posts...")
    
    latest_article = fetch_latest_article()
    if not latest_article:
        print("✅ Website check complete. No new articles found.")
        return

    last_post_url = read_last_post()

    if latest_article["link"] != last_post_url:
        print(f"✅ New post found: {latest_article['title']}")
        print(f"📌 Link: {latest_article['link']}")
        send_discord_notification(latest_article)
        save_last_post(latest_article["link"])
    else:
        print("✅ Website check complete. No new articles found.")

if __name__ == "__main__":
    check_for_updates()
