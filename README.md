## Chinese(s) Translator 中譯中翻譯器

Speak Like A Native Chinese 像中文母語者一樣說話

This project is a translator website powered by DeepSeek API.  
本專案是使用 DeepSeek API 的翻譯網站。

### Features 功能

- English <-> Chinese translation 中英文雙向翻譯
- Chinese output variants 中文輸出變體：
  - Mainland China 中國大陸 (`zh_cn`)
  - Taiwan 台灣 (`zh_tw`)
  - Hong Kong Written Chinese 香港書面中文 (`zh_hk_written`)
  - Hong Kong Spoken Cantonese 香港口語粵語 (`zh_hk_spoken`)
- Style options 風格選項：natural, formal, friendly, social (emoji-friendly)
- Auto detect source language 自動偵測來源語言

## Architecture 架構

- Frontend 前端：static site (`index.html`, `style.css`, `script.js`) hosted on GitHub Pages
- Backend 後端：Flask API (`api/index.py`) deployed on Vercel to protect `DEEPSEEK_API_KEY`

```json
{
  "text": "Can you help me fix this bug?",
  "source_language": "auto",
  "target_variant": "zh_hk_spoken",
  "tone_style": "friendly"
}
```

## Credits 致謝

This machine is created with the assistance of Cursor.  
本專案在 Cursor 的協助下完成網站開發。

