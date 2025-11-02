# Custom Domain Deployment Guide

## Overview

You want your dashboard accessible via a custom domain (e.g., `yourtradingbot.com`) instead of a random IP or ngrok URL. Here's how:

---

## Architecture

```
┌─────────────────┐
│  Custom Domain  │ ← Users visit this
│  yourdomain.com │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│   DreamHost     │────►│   Your       │
│   (Frontend)    │     │   Computer   │
│   Static Files  │     │   (Backend)  │
└─────────────────┘     └──────────────┘
         │                     ▲
         │                     │
         └─────────────────────┘
            ngrok Tunnel
         (secure connection)
```

**Key Point:** The backend with API keys runs on YOUR computer, not on DreamHost.

---

## Step-by-Step Setup

### Step 1: Buy and Configure Domain

1. **Buy domain on Namecheap**
   - Choose a domain (e.g., `astradingbot.com`, `cryptovibe.com`, etc.)
   - Add to cart and checkout
   - Domain will be ~$12-15/year

2. **Point domain to DreamHost**
   - In Namecheap: Go to your domain → DNS Management
   - Find "Nameservers" section
   - Change to "Custom DNS"
   - Add DreamHost nameservers (get these from your DreamHost control panel):
     - `ns1.dreamhost.com`
     - `ns2.dreamhost.com`
     - `ns3.dreamhost.com`
   - Click "Save"

   ⏳ **Wait 24-48 hours** for DNS to propagate

3. **Connect domain in DreamHost**
   - Log into DreamHost control panel
   - Go to "Domains" → "Manage Domains"
   - Click "Add Hosting to a Domain"
   - Enter your domain (e.g., `yourtradingbot.com`)
   - Create the domain

---

### Step 2: Set Up Backend Tunnel

The backend needs to be accessible from the internet, but we'll keep API keys safe on your computer.

#### Option A: ngrok (Easiest - $8/month)

```bash
# Install ngrok
winget install ngrok

# Start your backend (in one terminal)
python dashboard_api/run_server.py

# Start ngrok tunnel (in another terminal)
ngrok http 8000
```

You'll get a URL like: `https://abc123def456.ngrok.io`

**For persistent URL (recommended for contest):**
- Sign up for ngrok paid ($8/month)
- Create a "reserved domain" in ngrok dashboard (e.g., `yourbot.ngrok.io`)
- Use: `ngrok http 8000 --domain=yourbot.ngrok.io`

#### Option B: Cloudflare Tunnel (Free forever)

```bash
# Install cloudflared
winget install Cloudflare.cloudflared

# Start tunnel
cloudflared tunnel --url http://localhost:8000
```

You'll get a URL like: `https://random-subdomain.cfargotunnel.com`

**Note:** With Cloudflare Tunnel, you'll need to update your frontend config every time you restart (new random URL).

**Better:** Configure a custom domain with Cloudflare (requires moving DNS to Cloudflare):
1. Point your Namecheap domain to Cloudflare
2. Use Cloudflare Tunnel with your custom domain
3. Free, permanent URL

---

### Step 3: Build Frontend with Custom API URL

Create `dashboard/.env.production`:

```bash
# Use your ngrok URL (get this from Step 2)
VITE_API_BASE_URL=https://yourbot.ngrok.io
# OR if using Cloudflare Tunnel:
VITE_API_BASE_URL=https://random-subdomain.cfargotunnel.com
```

Build the dashboard:

```bash
cd dashboard
npm run build
```

This creates a `dist/` folder with static files.

---

### Step 4: Deploy to DreamHost

**Via FTP:**

1. Download FileZilla (free FTP client)
2. Connect to DreamHost:
   - Host: `ftp.dreamhost.com` or `yourdomain.com`
   - Username: Your DreamHost FTP username
   - Password: Your DreamHost FTP password
3. Navigate to `yourdomain.com/public_html`
4. Upload ALL contents of `dist/` folder
5. Make sure `index.html` is in the root of `public_html`

**Via DreamHost File Manager:**

1. Log into DreamHost control panel
2. Go to "Web Files" → "File Manager"
3. Navigate to `yourdomain.com/public_html`
4. Upload contents of `dist/` folder
5. Extract if needed

**Via SSH (if you have shell access):**

```bash
# Connect to DreamHost
ssh yourusername@yourdomain.com

# Navigate to web directory
cd ~/yourdomain.com/public_html

# Upload your dist/ folder (use scp or ftp)
# Then ensure all files are in place
ls -la
```

---

### Step 5: Test It

1. Visit `https://yourdomain.com`
2. Check browser console (F12) for any errors
3. Verify data is loading

**Common Issues:**

**"Cannot connect to API"**
- Check your ngrok tunnel is running
- Verify `VITE_API_BASE_URL` in `.env.production` is correct
- Rebuild and re-upload if you changed the URL

**"Dashboard shows but no data"**
- Check backend is running on your computer
- Check ngrok tunnel is active
- Check browser console for errors

**"Invalid CORS"**
- Backend already has CORS enabled
- If still issues, check ngrok URL is correct

---

### Step 6: HTTPS Setup

**DreamHost provides FREE SSL automatically!**

1. In DreamHost control panel
2. Go to "Domains" → "Manage Domains"
3. Click your domain
4. Click "Add SLL Certificate"
5. Select "Let's Encrypt" (FREE)
6. Click "Add Certificate"
7. Select "Force HTTPS" once SSL is active

Your site will now be accessible at `https://yourdomain.com` with a valid SSL certificate!

---

## Security Reminder

✅ **SAFE:**
- Frontend files on DreamHost (just HTML/CSS/JS)
- Backend on your computer with API keys
- Connection via ngrok/Cloudflare tunnel

❌ **UNSAFE:**
- Deploying backend code to DreamHost shared hosting
- Uploading `.env` file to DreamHost
- Storing API keys on any public server

---

## Cost Summary

| Item | Cost |
|------|------|
| Domain (Namecheap) | $12-15/year |
| DreamHost hosting | Already have it! ✅ |
| ngrok (optional) | $8/month (paid) or FREE |
| Cloudflare Tunnel | FREE |
| SSL certificate | FREE (Let's Encrypt) |
| **Total** | **$0-8/month** |

---

## Maintenance

### When Your Computer Restarts:

1. Start backend: `python dashboard_api/run_server.py`
2. Start ngrok: `ngrok http 8000`
3. Check the URL hasn't changed (if using paid ngrok, it won't)
4. If URL changed, update `dashboard/.env.production` and rebuild

### To Update Dashboard:

```bash
cd dashboard
npm run build
# Upload new dist/ folder contents to DreamHost
```

---

## Quick Command Reference

### Start Everything:
```bash
# Terminal 1: Backend
python dashboard_api/run_server.py

# Terminal 2: Tunnel
ngrok http 8000

# Terminal 3: When ready to update frontend
cd dashboard
echo "VITE_API_BASE_URL=https://yourbot.ngrok.io" > .env.production
npm run build
# Then upload dist/ to DreamHost
```

### Check Status:
```bash
# Check if backend is running
curl http://localhost:8000/api/status

# Check if ngrok is working
curl https://yourbot.ngrok.io/api/status
```

---

## For the Contest

**Recommended Setup:**
1. Use **ngrok paid** ($8 for one month during contest)
   - Get persistent URL
   - More reliable
   - Professional presentation

2. OR use **Cloudflare Tunnel** (FREE)
   - Set up custom domain with Cloudflare
   - Free, permanent solution
   - Takes 30 minutes to configure

Both options keep your API keys secure on your local machine!

---

## Next Steps

1. ✅ Buy domain on Namecheap
2. ✅ Point it to DreamHost
3. ✅ Start ngrok/Cloudflare tunnel
4. ✅ Build and deploy frontend
5. ✅ Test at your custom domain
6. ✅ Enable HTTPS (DreamHost makes this easy)
7. ✅ Share your URL for the contest!

Need help with any specific step? Let me know!




