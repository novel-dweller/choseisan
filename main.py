import os
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import gspread
from oauth2client.service_account import ServiceAccountCredentials


# ======================================
# .env 読み込み
# ======================================
load_dotenv()

CHOUSEISAN_URL = os.getenv("CHOUSEISAN_URL")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDENTIAL_JSON = os.getenv("CREDENTIAL_JSON")

# 必須チェック
if not CHOUSEISAN_URL:
    raise ValueError("CHOUSEISAN_URL が設定されていません。")
if not SPREADSHEET_ID:
    raise ValueError("SPREADSHEET_ID が設定されていません。")
if not CREDENTIAL_JSON:
    raise ValueError("CREDENTIAL_JSON が設定されていません。")

# ======================================
# Selenium（Selenium 4）
# ======================================
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

driver.get(CHOUSEISAN_URL)
wait = WebDriverWait(driver, 20)

# table 取得
table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
rows = table.find_elements(By.TAG_NAME, "tr")

data = []

for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    if not cells:
        cells = row.find_elements(By.TAG_NAME, "th")

    row_data = []

    for cell in cells:
        text = cell.text.strip()

        # テキストがある場合はそのまま
        if text:
            row_data.append(text)
            continue

        # img をチェック（○△×は画像）
        img_elems = cell.find_elements(By.TAG_NAME, "img")

        if img_elems:
            src = img_elems[0].get_attribute("src")

            if "mark-ok" in src:
                row_data.append("〇")
            elif "mark-tri" in src:
                row_data.append("△")
            elif "mark-x" in src:
                row_data.append("×")
            else:
                row_data.append("")
        else:
            row_data.append("")

    data.append(row_data)

driver.quit()


# ======================================
# Google Sheets（Drive API 不要）
# ======================================
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_JSON, scope)
client = gspread.authorize(creds)

sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# 実行前にクリア
sheet.clear()

sheet.update("A1", data)

print("スプレッドシートへの書き込みが完了しました！")
