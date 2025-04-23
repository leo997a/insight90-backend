from fastapi import FastAPI, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import os

app = FastAPI()

@app.get("/extract")
async def extract_match_dict(match_url: str):
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        chrome_options.binary_location = os.getenv("GOOGLE_CHROME_BIN", "/usr/bin/google-chrome")
        service = Service(os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver"))
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get(match_url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, 'script'))
        )
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        element = soup.find(lambda tag: tag.name == 'script' and 'matchCentreData' in tag.text)
        
        if not element:
            raise HTTPException(status_code=404, detail="لم يتم العثور على matchCentreData في الصفحة")
        
        matchdict = json.loads(element.text.split("matchCentreData: ")[1].split(',\n')[0])
        return matchdict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ أثناء استخراج البيانات: {str(e)}")
    finally:
        if driver is not None:
            try:
                driver.quit()
            except:
                pass
