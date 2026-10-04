# Video Manager

一個以 FastAPI 製作的輕量媒體管理工具，可在瀏覽器中整理本機影片、圖片與音樂，也能透過 OAuth 連結 Google Drive、OneDrive 和 Dropbox。

## 功能

- 上傳、搜尋、預覽及刪除本機媒體
- 在瀏覽器中播放影片與 MP3、瀏覽圖片
- 為影片指定顯示縮圖與背景音樂關聯
- 透過 `yt-dlp` 將 YouTube 內容下載為 MP4 或 MP3
- 連結 Google Drive、OneDrive 與 Dropbox
- 瀏覽雲端資料夾、串流媒體及上傳檔案
- 將雲端媒體儲存到本機媒體庫
- 響應式介面、深色模式與鍵盤／ARIA 無障礙支援

> 背景音樂功能目前只記錄影片與音樂的關聯，不會重新編碼或把音軌合併進影片。

## 支援格式

| 類型 | 本機媒體格式 |
| --- | --- |
| 影片 | `.mp4`、`.mov`、`.mkv` |
| 圖片 | `.jpg`、`.jpeg`、`.png`、`.webp` |
| 音訊 | `.mp3` |

雲端瀏覽器也能辨識部分 `.webm` 影片與 `.gif` 圖片；能否預覽仍取決於瀏覽器及雲端服務。

## 環境需求

- Python 3.10 以上
- 可連線至 YouTube 或雲端服務的網路環境（僅在使用相關功能時需要）
- Google Drive、OneDrive 或 Dropbox 的 OAuth 應用程式憑證（選用）

## 快速開始

### Linux / macOS

```bash
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
./venv/bin/python -m uvicorn main:app --reload
```

以上指令直接使用虛擬環境內的 Python，不需要先執行 `source venv/bin/activate`，也不依賴系統是否提供 `python` 指令。如果 `python3 -m venv venv` 顯示缺少 `venv` 模組，Ubuntu／Debian 可先安裝 `python3-venv`。

### Windows PowerShell

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

啟動後開啟：

- 本機媒體庫：<http://127.0.0.1:8000/>
- 雲端媒體庫：<http://127.0.0.1:8000/cloud>
- FastAPI API 文件：<http://127.0.0.1:8000/docs>

若不需要自動重載，可移除 `--reload`。若要讓區域網路內其他裝置連線，可加入 `--host 0.0.0.0`；這會讓服務暴露給其他主機，使用前請先閱讀下方的安全注意事項。

## 雲端服務設定

雲端整合是選用功能；未設定 OAuth 時，本機媒體庫仍可正常使用。

第一次載入雲端功能時，程式會使用下列結構建立或讀取 `cloud_config.json`：

```json
{
  "google": {
    "client_id": "",
    "client_secret": "",
    "folder_id": "root"
  },
  "onedrive": {
    "client_id": "",
    "client_secret": "",
    "folder_path": ""
  },
  "dropbox": {
    "client_id": "",
    "client_secret": "",
    "folder_path": ""
  }
}
```

預設啟動位址使用以下 OAuth callback：

| 服務 | Callback URL |
| --- | --- |
| Google Drive | `http://127.0.0.1:8000/cloud/google/callback` |
| OneDrive | `http://127.0.0.1:8000/cloud/onedrive/callback` |
| Dropbox | `http://127.0.0.1:8000/cloud/dropbox/callback` |

如果變更主機、協定或連接埠，必須同步更新 OAuth 供應商後台登記的 callback URL。各平台的建立應用程式、權限與設定步驟請參閱 [CLOUD_SETUP.md](CLOUD_SETUP.md)。

OAuth token 會儲存在 `cloud_tokens.json`，並依瀏覽器 session 分開保存。這只是簡易的本機 session 隔離，不是完整的使用者帳號系統。

## 使用方式

### 本機媒體庫

1. 在首頁選擇一個或多個媒體檔案並上傳。
2. 使用搜尋欄依檔名篩選內容。
3. 影片可選擇媒體庫中的圖片作為縮圖，也可指定一個 MP3 作為背景音樂關聯。
4. 使用「開啟檔案」查看原始媒體，或使用「刪除」移除檔案。

上傳檔案會存入 `media/`。同名檔案不會被覆寫，而會自動加上 `_1`、`_2` 等編號。

### YouTube 下載

1. 在首頁展開「YouTube 下載」。
2. 貼上 `youtube.com`、`youtu.be` 或 `youtube-nocookie.com` 網址。
3. 選擇 MP4 或 MP3 後開始下載。

下載結果會存入 `media/`。轉檔所需的 FFmpeg 由 `imageio-ffmpeg` 提供。請只下載你有權保存的內容，並遵守來源網站的服務條款與所在地法律。

### 雲端媒體庫

1. 完成 `cloud_config.json` 設定。
2. 開啟 `/cloud`，選擇雲端服務並按「連結帳號」。
3. 完成 OAuth 授權後，即可瀏覽資料夾、預覽媒體及上傳檔案。
4. 支援的媒體可透過「儲存到本機媒體庫」下載至 `media/`。

雲端影片及音訊會經由本機 FastAPI 服務代理串流，並轉送瀏覽器的 Range 請求。

## 專案結構

```text
video-manager/
├── main.py                 # FastAPI 應用程式與本機媒體路由
├── thumbnail_map.py        # 縮圖關聯資料讀寫
├── cloud/
│   ├── config.py           # 雲端設定與 token 儲存
│   ├── providers.py        # Google、OneDrive、Dropbox API 實作
│   └── router.py           # 雲端頁面、OAuth、串流與上傳路由
├── templates/
│   ├── base.html           # 共用頁面框架
│   ├── index.html          # 本機媒體頁面
│   ├── cloud.html          # 雲端媒體頁面
│   ├── components.html     # 共用 Jinja 元件與 SVG 圖示
│   ├── app.js              # 前端互動
│   ├── theme.js            # 主題初始化
│   └── style.css           # 頁面樣式
├── tests/test_ui.py        # 模板與表單契約回歸測試
├── media/                  # 本機媒體檔案
├── requirements.txt        # Python 套件依賴
└── CLOUD_SETUP.md          # 雲端 OAuth 詳細設定
```

執行期間還會使用以下資料檔案：

- `bgm_map.json`：影片與背景音樂的關聯
- `thumbnail_map.json`：本機及雲端影片的縮圖關聯
- `cloud_config.json`：OAuth 應用程式設定
- `cloud_tokens.json`：各瀏覽器 session 的 OAuth token

## 測試

執行不需要網路或雲端憑證的 UI 回歸測試：

```bash
./venv/bin/python -m unittest discover -s tests -v
```

測試會檢查模板是否可正常渲染、HTML ID 與 ARIA 關聯、靜態資源、表單欄位契約、輸出跳脫及刪除後的捲動位置還原。

## 主要路由

| 方法 | 路徑 | 用途 |
| --- | --- | --- |
| `GET` | `/` | 本機媒體庫 |
| `POST` | `/upload` | 上傳本機媒體 |
| `POST` | `/download-youtube` | 下載 YouTube MP4／MP3 |
| `POST` | `/assign-thumbnail` | 指定本機影片縮圖 |
| `POST` | `/assign-bgm` | 指定影片的背景音樂關聯 |
| `POST` | `/delete` | 刪除本機媒體 |
| `GET` | `/cloud` | 雲端媒體庫 |
| `GET` | `/cloud/{provider}/auth` | 啟動 OAuth 授權 |
| `GET` | `/cloud/{provider}/callback` | 接收 OAuth callback |
| `POST` | `/cloud/{provider}/upload` | 上傳至雲端 |
| `POST` | `/cloud/{provider}/save-to-media` | 將雲端檔案存到本機 |

`provider` 可使用 `google`、`onedrive` 或 `dropbox`。

## 安全注意事項

- 不要提交或分享 `cloud_config.json`、`cloud_tokens.json` 或其他憑證檔案。
- 若憑證或 token 曾被提交至版本控制，僅從 Git 刪除並不足夠；請到對應平台撤銷並重新產生。
- 此專案沒有完整的登入、權限管理、CSRF 防護、上傳容量限制或正式環境強化，預設較適合可信任的本機環境。
- 對外或區域網路公開前，應加入反向代理、HTTPS、身份驗證、請求大小限制與適當的檔案備份策略。
- `media/`、關聯 JSON 與 token 檔案都是執行期資料；升級或搬移專案前請先備份。

## 常見問題

### 連接埠 8000 已被占用

改用其他連接埠：

```bash
./venv/bin/python -m uvicorn main:app --reload --port 8001
```

若有使用雲端 OAuth，請同步修改供應商後台的 callback URL。

### 雲端服務顯示尚未設定

確認 `cloud_config.json` 中對應服務的 `client_id` 與 `client_secret` 均已填寫，並重新整理 `/cloud`。

### YouTube 下載失敗

確認網址屬於支援的 YouTube 網域、影片可公開觀看，並更新依賴：

```bash
./venv/bin/python -m pip install --upgrade yt-dlp imageio-ffmpeg
```

