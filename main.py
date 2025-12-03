import os
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import time

# ======================================
# .env 読み込み
# ======================================
load_dotenv()

CHOUSEISAN_URL = os.getenv("CHOUSEISAN_URL")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
CREDENTIAL_JSON = os.getenv("CREDENTIAL_JSON")

# 環境値が取得できているかチェック（任意）
if not CHOUSEISAN_URL:
    raise ValueError("CHOUSEISAN_URL が .env に設定されていません。")
if not SPREADSHEET_NAME:
    raise ValueError("SPREADSHEET_NAME が .env に設定されていません。")
if not CREDENTIAL_JSON:
    raise ValueError("CREDENTIAL_JSON が .env に設定されていません。")

# ======================================
# Selenium
# ======================================
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.get(CHOUSEISAN_URL)

wait = WebDriverWait(driver, 20)

table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
rows = table.find_elements(By.TAG_NAME, "tr")

data = []
for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    if len(cells) == 0:
        cells = row.find_elements(By.TAG_NAME, "th")
    data.append([cell.text.strip() for cell in cells])

driver.quit()

# ======================================
# Google Sheets
# ======================================
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_JSON, scope)
client = gspread.authorize(creds)

sheet = client.open(SPREADSHEET_NAME).sheet1
sheet.clear()
sheet.update("A1", data)

print("スプレッドシートへの書き込みが完了しました！")
