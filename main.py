import os
import requests
import yfinance as yf
from dotenv import load_dotenv


load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
RECIPIENT = os.getenv("RECIPIENT")

STOCK = "GOLDBEES.NS"
COMPANY = "Gold ETF India"

# ---------------- STOCK DATA ---------------- #

try:
    stock = yf.Ticker(STOCK)
    history = stock.history(period="5d")

    if history.empty:
        print("❌ No stock data found.")
        exit()

    today = history["Close"].iloc[-1]
    yesterday = history["Close"].iloc[-2]

    change = ((today - yesterday) / yesterday) * 100

    arrow = "🔺" if change >= 0 else "🔻"

    message = f"""📈 Stock Alert

Stock: {STOCK}
Price: ₹{today:.2f}
Change: {arrow} {abs(change):.2f}%

"""

except Exception as e:
    print("Stock Error:", e)
    exit()

# ---------------- NEWS ---------------- #

message += "📰 Latest News\n\n"

try:
    news_url = "https://newsapi.org/v2/everything"

    params = {
        "q": COMPANY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 3,
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(news_url, params=params)
    data = response.json()

    if data.get("status") == "ok":

        articles = data.get("articles", [])

        if len(articles) == 0:
            message += "No recent news found.\n"

        else:
            for article in articles:
                title = article.get("title", "No Title")
                url = article.get("url", "")

                message += f"• {title}\n{url}\n\n"

    else:
        message += f"News API Error: {data.get('message')}\n"

except Exception as e:
    message += f"News Error: {e}\n"

print(message)

# ---------------- WHATSAPP ---------------- #

url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

headers = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": RECIPIENT,
    "type": "text",
    "text": {
        "preview_url": False,
        "body": message
    }
}

try:
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    print("\nStatus Code:", response.status_code)
    print(response.text)

    if response.status_code == 200:
        print("\n✅ WhatsApp message sent successfully!")
    else:
        print("\n❌ Failed to send WhatsApp message.")

except Exception as e:
    print("WhatsApp Error:", e)