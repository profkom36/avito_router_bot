import requests
import time
from bs4 import BeautifulSoup

# === НАСТРОЙКИ ===
AVITO_URL = "https://www.avito.ru/all?q=роутер+билайн"
BOT_TOKEN = "ВСТАВЬ_СВОЙ_ТОКЕН_БОТА"  # токен от @BotFather
CHAT_ID = "ВСТАВЬ_СВОЙ_TELEGRAM_ID"   # твой Telegram ID
CHECK_INTERVAL = 300  # каждые 5 минут (300 секунд)

# === ФУНКЦИИ ===
def get_ads():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(AVITO_URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    ads = []
    for item in soup.select('[data-marker="item"]'):
        title = item.select_one('[itemprop="name"]')
        link = item.select_one("a")
        price = item.select_one('[itemprop="price"]')
        img_tag = item.select_one("img")

        if title and link:
            ads.append({
                "title": title.text.strip(),
                "link": "https://www.avito.ru" + link["href"],
                "price": price["content"] if price else "нет цены",
                "image": img_tag["src"] if img_tag and img_tag.get("src") else None
            })
    return ads

def send_message_with_photo(ad):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    caption = f"🆕 {ad['title']}\n💰 {ad['price']} ₽\n🔗 {ad['link']}"
    data = {"chat_id": CHAT_ID, "caption": caption}

    if ad["image"]:
        data["photo"] = ad["image"]
    else:
        # если нет фото, просто отправляем текст
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": caption}

    requests.post(url, data=data)

# === ОСНОВНОЙ ЦИКЛ ===
def main():
    seen_links = set()
    message = "✅ Бот запущен. Отслеживаю объявления 'роутер Билайн' по всей России."
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                  data={"chat_id": CHAT_ID, "text": message})
    
    while True:
        try:
            ads = get_ads()
            for ad in ads:
                if ad["link"] not in seen_links:
                    seen_links.add(ad["link"])
                    send_message_with_photo(ad)
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            err_msg = f"⚠️ Ошибка: {e}"
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                          data={"chat_id": CHAT_ID, "text": err_msg})
            time.sleep(60)

if __name__ == "__main__":
    main()
