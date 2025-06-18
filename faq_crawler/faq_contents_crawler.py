import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ブラウザ設定
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# faq_result_2.csvで実行するよ
with open("faq_result_2.csv", "r", encoding="utf-8") as f:
    reader = list(csv.reader(f, delimiter='\t'))

# 列に名前がついていない場合はつける
if len(reader[0]) < 5:
    reader[0] += ["Text", "HasImage"]

# B2:B400 の URL一個づつみる
for i in range(1, min(len(reader), 401)):  # 0行目をスキップ
    url = reader[i][1]  

    print(f"🌐 now visiting {i+1} 件目のURL: {url}")
    try:
        driver.get(url)
        time.sleep(2)

        try:
            content_div = driver.find_element(By.CLASS_NAME, "tinymce-content")
            text = content_div.text.strip()
            has_image = "img" in content_div.get_attribute("innerHTML")
        except:
            text = "[コンテンツ見つからないよー（ ;  ; ）]"
            has_image = False

    except Exception as e:
        print(f"⚠️ {i+1} 行目 アクセス失敗: {e}")
        text = "[アクセス失敗]"
        has_image = False

    while len(reader[i]) < 5:
        reader[i].append("")

    reader[i][3] = text
    reader[i][4] = str(has_image)

# csvに書き込み
with open("faq_result_2.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerows(reader)

driver.quit()
print("✅ 中身と画像ファイルの有無の確認結果をfaq_result_2.csvに書き込んだよ 🐣")

