from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

category_ids = [
    "kb-index__category-96270652585",
    "kb-index__category-96270652588",
    "kb-index__category-183209302874",
    "kb-index__category-109588216638",
    "kb-index__category-96270652591",
    "kb-index__category-99253856275",
    "kb-index__category-99517563170",
    "kb-index__category-124236221025",
    "kb-index__category-123975591959",
    "kb-index__category-180106123880",
    "kb-index__category-96273009811"
]

# ブラウザ設定
options = Options()
options.add_argument('--headless')  
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_category(driver, category_id, global_index, writer):
    print(f"\n👉 トップページに戻りました。次はこれを処理する：{category_id}")
    driver.get("https://knowledge.squadbeyond.com/")
    time.sleep(2)

    try:
        category = driver.find_element(By.CSS_SELECTOR, f'a#{category_id}')
        driver.execute_script("arguments[0].click();", category)
        print(f"✅ クリックできた：{category_id}")
        time.sleep(2)
    except:
        print(f"❌ category_id見つからなかった： {category_id}、スキップする")
        return global_index

    # “さらに表示” 10回まで
    show_more_clicks = 0
    for _ in range(10):
        try:
            show_more = driver.find_element(By.XPATH, '//div[@class="content-container"]//a[contains(text(), "さらに表示")]')
            show_more.click()
            show_more_clicks += 1
            print(f"🔄 クリック『さらに表示』 第 {show_more_clicks} 回")
            time.sleep(1)
        except:
            print("🚪 No more『さらに表示』")
            break

    # 件数を探す
    faq_items = driver.find_elements(By.XPATH, '//div[@class="kb-categories"]//li/a')
    print(f"📋 find {len(faq_items)} 件目")

    for item in faq_items:
        href = item.get_attribute('href')
        try:
            WebDriverWait(driver, 2).until(lambda d: item.text.strip() != "")
            text = item.text.strip()
        except:
            text = "[読み込みできなかった]"
        writer.writerow([global_index, href, text])
        print(f"📝 {global_index}. {text} -> {href}")
        global_index += 1
    return global_index

# 主流程
try:
    with open("faq_result.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(["No", "URL", "Title"])
        index = 1
        for cat_id in category_ids:
            index = scrape_category(driver, cat_id, index, writer)
finally:
    driver.quit()
    print("\n🏁 できたよ。faq_result.csvを確認してね。")
