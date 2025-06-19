import os
import time
import requests
import io
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


# ⏱️  先月の年月を取得
today = datetime.today()
first_day_of_this_month = today.replace(day=1)
last_month = first_day_of_this_month - timedelta(days=1)
search_keyword = last_month.strftime("%Y/%m")
print(f"🔍 検索キーワード: {search_keyword}")

# --- フォルダ設定（名前, Google Drive フォルダID）---
folder_targets = [
    ("広告用簡易LP", "1sBlslUkpFBl0aSlvykCV6NtJgK6ldyxl"),
    ("PLUESTクレンズセラムセット", "1NZ3_e7DePkxI053nqKnBQX56Brpv9RLX")
]

# --- 認証設定 ---
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_FILE = "jingjings-databace-d96f3d3f4fe6.json"
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive = build('drive', 'v3', credentials=creds)

# --- 各フォルダ処理 ---
for name, folder_id in folder_targets:
    print(f"\n📂 フォルダ開始：{name}")
    output_dir = os.path.join("exports", name)
    os.makedirs(output_dir, exist_ok=True)

    query = f"'{folder_id}' in parents and trashed=false"
    resp = drive.files().list(q=query, fields="files(id, name, mimeType)").execute()
    items = resp.get("files", [])

    if not items:
        print(f"⚠ {name} は中身ゼロ件か非共有です。")
        continue

    for item in items:
        fid = item['id']
        fname = item['name']
        mime = item['mimeType']
        safe_name = fname.replace("/", "_").replace("\\", "_")
        out_path = os.path.join(output_dir, f"{search_keyword}_{safe_name}.pdf")

        try:
            if mime in (
                "application/vnd.google-apps.document",
                "application/vnd.google-apps.spreadsheet",
                "application/vnd.google-apps.presentation"
            ):
                export_url = f"https://docs.google.com/drive/u/0/export?id={fid}&exportFormat=pdf"
                creds.refresh(Request())
                headers = {"Authorization": f"Bearer {creds.token}"}
                r = requests.get(export_url, headers=headers)
                if r.status_code == 200:
                    with open(out_path, "wb") as f:
                        f.write(r.content)
                    print(f"✔ 保存しました（変換）: {out_path}")
                else:
                    print(f"✘ 取得に失敗：{out_path} (HTTP {r.status_code})")
            else:
                request = drive.files().get_media(fileId=fid)
                fh = io.FileIO(out_path, mode='wb')
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                fh.close()
                print(f"✔ 通常ファイルを保存：{out_path}")

            time.sleep(1)
        except Exception as e:
            print(f"❌ エラー：{fname} → {e}")

print("\n🎉 すべてのフォルダ処理が完了しました！")
