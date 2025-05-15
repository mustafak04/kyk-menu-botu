from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from twilio.rest import Client
from webdriver_manager.chrome import ChromeDriverManager
import datetime
import sys
import time
import os

def get_daily_menu():
    driver = None
    try:
        # Chrome ayarları
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--headless")

        # Tarayıcıyı başlat (kesin çalışan versiyon)
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Sayfayı aç
        driver.get("https://kykyemek.com/Menu/TodayMenu")
        print("Sayfa yüklendi")

        # Şehir seçimi (İzmir)
        city_select = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[1]/div[1]/select"))
        )
        Select(city_select).select_by_visible_text("İzmir")
        print("İzmir seçildi")

        # Kahvaltı menüsü (verdiğiniz XPath)
        breakfast_div = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[1]/div[2]/div/div/div/div[1]/div/div[2]/div[1]"))
        )
        breakfast_items = [p.text for p in breakfast_div.find_elements(By.TAG_NAME, "p") if p.text.strip()]
        print("Kahvaltı menüsü alındı")

        # Akşam yemeği (verdiğiniz XPath)
        dinner_div = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[1]/div[2]/div/div/div/div[3]/div/div[2]/div[1]"))
        )
        dinner_items = [p.text for p in dinner_div.find_elements(By.TAG_NAME, "p") if p.text.strip()]
        print("Akşam yemeği alındı")

        # Mesaj formatı
        message = f"🍳 *Kahvaltı* ({datetime.date.today().strftime('%d.%m.%Y')}):\n"
        message += "\n".join(breakfast_items) + "\n\n"
        message += f"🌙 *Akşam Yemeği*:\n" + "\n".join(dinner_items)
        
        return message
        
    except Exception as e:
        if driver:
            driver.save_screenshot("error.png")
            print("Hata ekran görüntüsü kaydedildi: error.png")
        raise Exception(f"Scraping hatası: {str(e)}")
    finally:
        if driver:
            driver.quit()

def send_whatsapp(message):
    try:
        # Twilio ayarları (kendi bilgilerinizle değiştirin)
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        to_number = os.getenv("WHATSAPP_TO")
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=message,
            from_='whatsapp:+14155238886',
            to=to_number
        )
        return True
    except Exception as e:
        raise Exception(f"Twilio hatası: {str(e)}")

def log_message(status, content=""):
    with open("kyk_bot_log.txt", "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        f.write(f"[{timestamp}] {status}: {content}\n")

if __name__ == "__main__":
    try:
        print("Program başlatıldı...")
        menu = get_daily_menu()
        print("Menü başarıyla alındı!")
        result = send_whatsapp(menu)
        if result:
            log_message("SUCCESS", "Menü gönderildi")
            print("WhatsApp'a gönderildi!")
        else:
            log_message("ERROR", "Gönderim başarısız")
    except Exception as e:
        log_message("CRITICAL", str(e))
        print("Hata oluştu:", str(e))
        sys.exit(1)