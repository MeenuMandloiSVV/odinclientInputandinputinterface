# 🚀 Deployment Guide - Streamlit Cloud

Deploy your Odin Trading Platform app for **FREE** with shareable links

---

## ✅ Prerequisites

- ✅ GitHub account (free)
- ✅ Streamlit Cloud account (free, uses GitHub login)
- ✅ MongoDB connection URI with credentials
- ✅ Odin API credentials

---

## 📋 Step-by-Step Deployment

### Step 1: Prepare Your Repository

**1.1 Update `.gitignore`**
Already done! Ensures `secrets.toml` is never committed.

**1.2 Verify Files**
```bash
git status
```
Should show:
- ✅ app.py
- ✅ requirements.txt
- ✅ pages/
- ✅ modules/
- ✅ .streamlit/config.toml
- ❌ .streamlit/secrets.toml (NOT committed)

**1.3 Update requirements.txt**
Already includes:
- streamlit==1.44.1
- pymongo==4.6.1
- motor==3.7.1
- pyotp==2.9.0
- And others...

### Step 2: Push to GitHub

```bash
# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Odin Trading Platform - Login & Strategy Selection System"

# Push to GitHub
git push -u origin main
```

**👉 Make sure `.streamlit/secrets.toml` is NOT in the commit!**

### Step 3: Connect Streamlit Cloud

**3.1 Go to Streamlit Cloud**
- Visit https://share.streamlit.io
- Click "Sign in with GitHub"
- Authorize Streamlit to access your repos

**3.2 Create New App**
- Click "New App" button
- Select your repository
- Select branch: **main**
- Set main file path: **`app.py`**
- Click "Deploy"

**3.3 Wait for Deployment**
- Streamlit will build your app (2-5 minutes)
- You'll get a public shareable link! 🎉

---

## 🔐 Add Secrets to Streamlit Cloud

**Important:** Credentials go into Streamlit Cloud, NOT your GitHub repo

### 4.1 Access Secrets

1. Go to your app on Streamlit Cloud
2. Click the three-dot menu ⋮ (top right)
3. Select "Settings"
4. Click "Secrets"

### 4.2 Add Your Secrets

Copy and paste into the Secrets editor:

```toml
[mongodb]
uri = "mongodb+srv://username:password@cluster.mongodb.net/?tls=true&tlsAllowInvalidCertificates=true"

[odin]
api_url = "https://your-odin-api-domain.com"
api_key = "your-actual-api-key"
```

### 4.3 Save & Deploy

- Click "Save"
- App auto-redeploys with secrets
- You're done! ✅

---

## 🌐 Share Your App

Your app is now **live with a public link!**

### Get Shareable Link
1. Top of Streamlit Cloud app page
2. Copy the URL: `https://your-app-name.streamlit.app`
3. Share with team members!

### Team Access
- Anyone with the link can access
- No installation needed
- Works on mobile, tablet, desktop
- Secured by MongoDB credentials (never exposed)

---

## 🔄 Updating Your App

### Update Code

```bash
# Make changes locally
# ...

# Commit
git add .
git commit -m "Update strategy mapping"

# Push
git push
```

Streamlit Cloud auto-detects changes → Auto-redeploys in ~1 minute!

### Update Secrets

1. Go to Streamlit Cloud app Settings
2. Edit Secrets
3. Click Save
4. App redeploys automatically

---

## ⚠️ Environment Variables Best Practices

### What to put in Secrets:
- ✅ MongoDB URI
- ✅ API Keys
- ✅ Database credentials
- ✅ Any sensitive data

### What NOT to put in Secrets:
- ❌ Strategy mappings (in code)
- ❌ Field configurations (in code)
- ❌ UI text (in code)

---

## 📊 Monitoring Your App

### View Logs
1. Streamlit Cloud dashboard
2. Click your app
3. Logs tab shows real-time output

### Check Status
- Green checkmark = Running
- Red indicator = Issues (check logs)
- Redeployment in progress = Shows status

### Restart App
1. Settings → Developer tools
2. Click "Reboot app"
3. App restarts (takes 10-30 seconds)

---

## 🆘 Troubleshooting Deployment

### Error: "ModuleNotFoundError"
→ Add missing package to `requirements.txt`:
```bash
pip install package-name
echo "package-name==version" >> requirements.txt
git add requirements.txt
git commit -m "Add dependency"
git push
```

### Error: "Missing secrets"
→ Check Streamlit Cloud Settings → Secrets are configured correctly
→ Verify all required keys are there:
- `mongodb.uri`
- `odin.api_url`
- `odin.api_key`

### Error: "Connection refused"
→ Check MongoDB URI is correct
→ Verify IP whitelist includes Streamlit Cloud:
- Go to MongoDB Atlas → Network Access
- Add IP: `0.0.0.0/0` (allows all, OR add specific Streamlit IPs)

### App slow to load
→ First load takes 30-60 seconds (normal)
→ Subsequent loads are cached

### Data not persisting
→ Check MongoDB is saving correctly
→ Verify user ID matches database name

---

## 💰 Costs

| Item | Cost |
|---|---|
| Streamlit Cloud | **FREE** ✅ |
| Custom domain | FREE (or $7/month for custom) |
| MongoDB Atlas | FREE tier up to 5GB |
| Total | **$0 for basic setup** |

---

## 🔒 Security Checklist

- ✅ Secrets in Streamlit Cloud (NOT in GitHub)
- ✅ `.gitignore` prevents accidental commits
- ✅ HTTPS/TLS enabled by default
- ✅ MongoDB credentials encrypted in transit
- ✅ TOTP verification for login
- ✅ No password storage in database
- ✅ Public link doesn't expose credentials

---

## 📱 Access From Anywhere

Your app is accessible from:
- ✅ Desktop browser (Chrome, Safari, Firefox, Edge)
- ✅ Mobile browser (iOS, Android)
- ✅ Tablet
- ✅ Smart TV (with web browser)

**No installation needed for users!**

---

## 🔗 Share with Team

```bash
# Get your app URL
https://your-app-name.streamlit.app

# Share as:
- Email: Copy link
- Slack: Paste in channel
- WhatsApp: Send link
- QR Code: Generate from browser
```

---

## 📊 Advanced: Custom Domain

Want your own domain like `trading.yourcompany.com`?

1. Streamlit Cloud Settings
2. Custom domain settings
3. Add your domain
4. Update DNS records
5. Click verify

Cost: $7/month with Streamlit (optional)

---

## 🎯 Performance Optimization

### For speed:
- Use `@st.cache_resource` for connections (done ✅)
- Use `@st.cache_data` for data (implement as needed)
- Limit MongoDB queries per page
- Compress images
- Use CDN for static assets

---

## 📞 Getting Help

### Streamlit Community
- https://discuss.streamlit.io
- Forum for issues & questions

### MongoDB Support
- https://docs.mongodb.com
- MongoDB Atlas console

### Your App Logs
- Real-time logs in Streamlit Cloud
- Shows every error and issue

---

## ✅ Deployment Checklist

- [ ] GitHub repository created & code pushed
- [ ] `.gitignore` includes `secrets.toml`
- [ ] `requirements.txt` updated with all dependencies
- [ ] Streamlit Cloud app created
- [ ] Secrets added (mongodb.uri, odin.api_url, odin.api_key)
- [ ] App deployed successfully (green checkmark)
- [ ] Tested login flow
- [ ] Tested strategy selection
- [ ] Tested form submission
- [ ] Shared link with team

---

## 🎉 Success!

Your app is now:
- ✅ **Live** on the internet
- ✅ **Shareable** with public link
- ✅ **Free** to run
- ✅ **Secure** with encrypted credentials
- ✅ **Accessible** from any device
- ✅ **Auto-updating** when you push code

**Deployed with Streamlit Cloud! 🚀**

---

**Questions?** Check the main README.md or Streamlit documentation
