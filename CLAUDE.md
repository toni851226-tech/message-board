# Project Notes

## 使用者工作偏好
- **自動接續中斷的工作**：如果工作中途因用量耗盡而中斷，用量恢復時應自動從中斷點繼續，不需要使用者再次提示。
- **進度回報使用中文**。
- **登入相關**：能自動完成的盡量自動完成，需要登入的部分開啟瀏覽器讓使用者自己登入。

## 部署資訊
- **平台**：Render (free tier)
- **Service ID**：`srv-d88qisfavr4c7392eovg`
- **公開 URL**：https://message-board-dyuw.onrender.com
- **GitHub**：toni851226-tech/message-board (branch: master)
- **自動部署**：push 到 master 會自動觸發 Render deploy

## 環境變數（Render 已設定）
- `GEMINI_API_KEY` — Google Gemini 2.5 Flash API key
- `APPS_SCRIPT_URL` — Google Apps Script Web App URL（透過 Gmail 寄信）
- `RECIPIENT_EMAIL` — 收件人 `t700@mdjh.tp.edu.tw`

## 技術重點
- Render 免費方案封鎖所有對外 SMTP（25/465/587），所以改用 HTTPS：Python → Google Apps Script `MailApp.sendEmail()` → Gmail。
- Apps Script Web App 對 POST 會回 302 redirect 到 `script.googleusercontent.com/macros/echo`，**httpx 0.27 預設不跟隨 redirect，必須加 `follow_redirects=True`**。
- Render Dashboard 的 Edit env vars UI 在 browser automation 下偶爾會凍結 tab。用 React 的 `nativeInputValueSetter` 加上 dispatch input/change events 可以正確更新 controlled input。

## Google Apps Script
- 帳號：sihsianclaude@gmail.com
- Project ID：`18RC5yM9NZpyvBjomhDEKh1f2lA49c7xy3VCqNCCn1Mq6JlaR2mF2gem1`
- 部署方式：Web App, 執行身分 sihsianclaude@gmail.com, 存取權「所有人」
- doPost 收 `{to, subject, body}` JSON，呼叫 `MailApp.sendEmail()`
