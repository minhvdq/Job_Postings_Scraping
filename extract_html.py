import time
import json
import pickle
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv, dotenv_values 

# loading variables from .env file
load_dotenv() 

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
COOKIES_PATH = os.getenv("COOKIES_PATH")

def check_cookies_exist() :
    if os.path.exists(f"./{COOKIES_PATH}"):
        try:
            with open(COOKIES_PATH, "rb") as f:
                cookies = pickle.load(f)
            
            # ✅ Ensure essential cookies exist
            required_cookies = ["li_at", "JSESSIONID"]
            saved_cookie_names = [cookie["name"] for cookie in cookies]

            if all(cookie in saved_cookie_names for cookie in required_cookies):
                print("✅ Valid cookies found. No need to log in again.")
                return True  # Cookies are valid
            else:
                print("⚠️ Cookies found but missing essential login cookies.")
                return False  # Cookies exist but are incomplete

        except Exception as e:
            print(f"❌ Error loading cookies: {e}")
            return False  # Corrupt or invalid cookies
    else:
        print("❌ No cookies file found.")
        return False  # No cookies file

def save_linkedin_cookies():
    if check_cookies_exist() : 
        print("✅ Using existing cookies. No need to log in manually.")
        return
    
    print("🔹 No valid cookies found. Please log in manually.")

    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # ✅ Step 1: Open LinkedIn Manually & Log In
    driver.get("https://www.linkedin.com/login")
    input("🔹 After logging in manually, press Enter to save cookies...")

    # ✅ Step 2: Save Cookies to a File
    cookies = driver.get_cookies()
    with open(COOKIES_PATH, "wb") as f:
        pickle.dump(cookies, f)

    print("✅ Cookies saved successfully! Now you can use them to log in automatically.")
    driver.quit()

def get_raw_html( url ) :
     # 🔹 Use Selenium to render JavaScript-loaded content
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print("🔹 Loading page with Selenium...")

        if( url.startswith("https://www.linkedin.com") ):

            save_linkedin_cookies()

            print("🔹 Authenticating LinkedIn With saved Cookies...")

            driver.get("https://www.linkedin.com/")
            time.sleep(3)

            # ✅ Step 2: Load Cookies from File
            with open(COOKIES_PATH, "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    driver.add_cookie(cookie)

            time.sleep(2)

        driver.get(url)
        time.sleep(2)  # Wait for JavaScript to load fully

        # 🔹 Extract the rendered HTML
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()  # Close the browser session
        
        raw_text = [element.get_text(separator=" ").strip().replace("\n", " ") for element in soup.find_all(['p', 'ul', 'li'])]
        return " ".join(raw_text)  # Returns a single clean string
    except Exception as e:
        print(f"❌ Selenium Error: {e}") 