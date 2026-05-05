## EN/ZH Variant Translator (DeepSeek)

This project is a web translator that supports:
- English <-> Chinese translation
- Chinese output variants:
  - Mainland China (`zh_cn`)
  - Taiwan (`zh_tw`)
  - Hong Kong Written Chinese (`zh_hk_written`)
  - Hong Kong Spoken Cantonese (`zh_hk_spoken`)
- Style options: natural, formal, friendly, social (emoji-friendly)

## Architecture

- Frontend: static site (`index.html`, `style.css`, `script.js`) for GitHub Pages
- Backend: Flask API (`api/index.py`) deployed on Vercel to keep your DeepSeek key secure

## 1) Deploy backend (Vercel)

1. Push this repository to GitHub.
2. Import the repo in Vercel.
3. In Vercel Project Settings -> Environment Variables, set:
   - `DEEPSEEK_API_KEY=your_key_here`
4. Deploy.
5. Copy your backend URL, for example:
   - `https://your-backend-domain.vercel.app`

## 2) Configure frontend API URL

Edit `script.js`:
- Change `API_BASE_URL` to your Vercel domain.

Example:
`const API_BASE_URL = "https://your-backend-domain.vercel.app";`

## 3) Deploy frontend (GitHub Pages)

Since this is a static frontend:
1. In GitHub, go to repository Settings -> Pages.
2. Set Source to `Deploy from a branch`.
3. Choose `main` branch and root (`/`).
4. Save, then open the Pages URL.

## API Request Format

`POST /api/translate`

```json
{
  "text": "Can you help me fix this bug?",
  "source_language": "auto",
  "target_variant": "zh_hk_spoken",
  "tone_style": "friendly"
}
```

