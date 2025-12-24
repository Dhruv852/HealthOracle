# 🔐 API Key Security Fix - URGENT

## ⚠️ Your API Key Was Leaked

Your Gemini API key was exposed in your repository and has been revoked by Google. Follow these steps to fix it:

---

## 📋 Steps to Fix

### 1. **Get a New Gemini API Key**

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the new API key (it will look like: `AIzaSy...`)

### 2. **Create a `.env` File Locally**

Create a file named `.env` in the project root directory:

```bash
cd /Users/dhruvtiwari/Desktop/healthoracle
nano .env
```

Add the following content (replace with your actual keys):

```env
# Django Secret Key
DJANGO_SECRET_KEY=django-insecure-t!-y&-7$irvlvl8_cza6c9soy(^8ptr+sm1(!7@2s0br^h56w2

# Gemini API Key - PASTE YOUR NEW KEY HERE
GEMINI_API_KEY=AIzaSy_YOUR_NEW_API_KEY_HERE
```

**Save and close** (Ctrl+X, then Y, then Enter)

### 3. **Restart the Development Server**

Stop the current server (Ctrl+C) and restart:

```bash
source venv/bin/activate
python manage.py runserver
```

### 4. **Update Render Environment Variables**

If you're deploying to Render:

1. Go to your [Render Dashboard](https://dashboard.render.com/)
2. Select your **healthoracle** service
3. Go to **Environment** tab
4. Update these variables:
   - `GEMINI_API_KEY`: Your new API key
   - `DJANGO_SECRET_KEY`: Generate a new one (optional but recommended)
5. Click **Save Changes**
6. Render will automatically redeploy

---

## ✅ What Was Fixed

1. ✅ Removed hardcoded API keys from `settings.py`
2. ✅ Removed hardcoded API keys from `render.yaml`
3. ✅ Added `python-dotenv` for loading `.env` files
4. ✅ Created `.env.example` as a template
5. ✅ `.env` is already in `.gitignore` (won't be committed)

---

## 🔒 Security Best Practices

### ✅ DO:
- Store API keys in `.env` file (local development)
- Use environment variables in production (Render, Railway, etc.)
- Keep `.env` in `.gitignore`
- Rotate API keys if they're exposed

### ❌ DON'T:
- Commit API keys to Git
- Share API keys in public repositories
- Hardcode secrets in source code
- Use the same API key across multiple projects

---

## 🚀 Quick Start After Fix

1. **Create `.env` file** with your new API key
2. **Restart server**: `python manage.py runserver`
3. **Test chatbot** at http://127.0.0.1:8000/chatbot/

---

## 📝 Generate a New Django Secret Key (Optional)

If you want a new Django secret key:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copy the output and add it to your `.env` file.

---

## 🆘 Troubleshooting

### Error: "GEMINI_API_KEY not set"
- Make sure `.env` file exists in project root
- Check that `GEMINI_API_KEY=...` is in the file
- Restart the server after creating `.env`

### Error: "403 PERMISSION_DENIED"
- Your API key is still the old leaked one
- Get a new API key from Google AI Studio
- Update `.env` with the new key

### Chatbot still not working
- Check that `python-dotenv` is installed: `pip list | grep dotenv`
- Verify `.env` file has no syntax errors
- Check server logs for specific error messages

---

## 📞 Need Help?

If you're still having issues:
1. Check the server logs for error messages
2. Verify your API key is valid at [Google AI Studio](https://aistudio.google.com/app/apikey)
3. Make sure you're using the correct API key format

---

**Last Updated**: 2025-12-24
