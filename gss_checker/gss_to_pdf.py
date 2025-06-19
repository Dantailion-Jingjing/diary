import os
import time
import io
import requests
from google.oauth2.service_account import Credentials
import gspread
from google.auth.transport.requests import Request  # リフレッシュ用に必要

# --- 認証設定。アカウントごとに取得する ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]
SERVICE_ACCOUNT_FILE = "jingjings-databace-d96f3d3f4fe6.json"

creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)


gc = gspread.authorize(creds)

# --- スプレッドシートを「ID」で開く ---
SPREADSHEET_ID = "1uCasC0K8lobS2jfgvaI5Xn25YFwzZtBV_BYQN6KTzJg"  # 👈 君のIDに置き換えろ
try:
    ss = gc.open_by_key(SPREADSHEET_ID)
except Exception as e:
    import traceback
    print(f"スプレッドシートを開けないよ。")
    traceback.print_exc()
    exit(1)

# --- 各シートをPDF化して保存 ---
def export_sheet_as_pdf(spreadsheet, worksheet, creds):
    sheet_title = worksheet.title
    gid = worksheet._properties['sheetId']

    export_url = (
        f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}/export"
        f"?format=pdf&portrait=false&fitw=true&gid={gid}"
    )

    # トークンのリフレッシュ
    creds.refresh(Request())

    headers = {"Authorization": f"Bearer {creds.token}"}
    r = requests.get(export_url, headers=headers)

    if r.status_code == 200:
        safe_title = sheet_title.replace("/", "_").replace("\\", "_")
        filename = f"{safe_title}.pdf"
        with open(filename, "wb") as f:
            f.write(r.content)
        print(f"✔ 保存しました：{filename}")
    else:
        print(f"✘ PDF取得に失敗：{sheet_title} (HTTP {r.status_code})")

# --- 全ワークシート処理 ---
for ws in ss.worksheets():
    print(f"→ 処理中：{ws.title}")
    export_sheet_as_pdf(ss, ws, creds)
    time.sleep(1)  # Googleに優しく

print("🎉 全部のシートをPDFにして保存完了。お疲れちゃん。")

