# Video Manager
================

A video manager for downloading, organizing, and playing videos.
## Google Drive 設定
----------------

1. 在 Google Cloud Console 啟用 **Google Drive API**，建立「OAuth 2.0 用戶端 ID」（Desktop app），並下載用戶端 JSON。
2. 使用你的 Google 帳號完成一次 OAuth 授權，取得 refresh token；EC2 以此 token 代表你的帳號存取 Drive。
3. 在 Google Drive 建立要存放媒體的資料夾，從資料夾網址取得 ID（`folders/` 後面的字串）。

在自己的電腦（不是 EC2）執行一次，瀏覽器會要求登入並授權，完成後終端機會輸出三個要放入 EC2 的密鑰：

## Prerequisites
----------------

*   Install the required packages:

