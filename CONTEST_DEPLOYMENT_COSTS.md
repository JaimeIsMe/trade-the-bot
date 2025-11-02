# Contest Deployment Cost Analysis

## Your Dashboard Traffic Pattern

### Per Viewer:
- **Dashboard loads:** ~500KB (React app + assets)
- **API calls every 10 seconds:**
  - `/api/portfolio/summary`: ~2KB
  - `/api/bots`: ~1KB
  - `/api/performance` (x5 bots): ~5KB
  - `/api/decisions` (x5): ~3KB
  - `/api/trades` (x5): ~20KB
  - `/api/positions`: ~2KB
- **Total per 10-second cycle:** ~33KB
- **Per hour per viewer:** ~11.9MB
- **Per day per viewer** (staying on page): ~285MB

### Contest Scenario Estimates:

**100 concurrent viewers, 1 hour viewing:**
- Total traffic: ~1.2GB
- Cost: Varies by solution

**500 concurrent viewers, 4 hours:**
- Total traffic: ~5.7GB
- Cost: Varies by solution

---

## Solutions & Costs

### Option 1: ngrok (✅ RECOMMENDED for Contest)

**Pricing:**
- **Free tier:** 40 connections/min, random URLs
- **Personal:** $8/month - 2 static domains, unlimited bandwidth
- **Team:** $10/user/month

**For the contest:**
- ✅ **FREE is enough** if you get a persistent domain
- ⚠️ **Note:** Free tier may have rate limits
- 💰 **Cost:** $0-8 for the month

**Recommendation:** Use ngrok free tier, just restart if the URL changes.

---

### Option 2: Cloudflare Tunnel (FREE, but more complex)

**Pricing:**
- **Cloudflare Tunnel** is **completely FREE**
- Unlimited bandwidth
- No rate limits
- However, you need to use **Cloudflare for your domain**

**Setup complexity:**
- Point your DreamHost domain to Cloudflare nameservers
- Then use cloudflared to tunnel to your local backend
- Takes ~30 minutes to set up

**Cost:** $0 forever

---

### Option 3: Tailscale (✅ EASIEST & FREE)

**What it is:** Creates a secure VPN between your computer and servers

**Pricing:**
- **FREE tier:** 1 user, up to 100 devices
- **Teams:** $7/user/month

**Setup:**
1. Install Tailscale on your computer
2. Deploy the dashboard as a static site on DreamHost
3. Configure the dashboard to connect via your Tailscale IP
4. Share your Tailscale IP with judges

**Cost:** $0

**Pros:**
- Very easy setup (5 minutes)
- Free
- Secure (only people you share with can access)
- Stable connection

---

### Option 4: Run Backend on a $5 VPS

**Providers:**
- DigitalOcean: $5/month
- Vultr: $4/month
- Linode: $5/month

**Setup:**
1. Deploy backend to VPS
2. Store `.env` file there securely
3. Deploy dashboard to DreamHost
4. Connect them

**Security:**
- ⚠️ Your API keys go to the cloud
- ⚠️ Have strong firewall rules
- ⚠️ Only expose necessary ports

**Cost:** $5/month

---

### Option 5: Railway / Render (Simplest Cloud Backend)

**Pricing:**
- Railway: $5/month + usage
- Render: Free tier available

**Setup:**
1. Deploy backend as a service
2. Upload `.env` to the platform
3. Deploy dashboard to DreamHost
4. Connect them

**Cost:** $5-20/month depending on traffic

---

## My Recommendations for the Contest

### For MAXIMUM Safety (Recommended):
**✅ Tailscale + DreamHost**
- Keep everything on your local machine
- Free
- 5-minute setup
- Judges connect to your Tailscale IP

**Cost:** $0 | **Time to setup:** 5 minutes

### For EASIEST Demo:
**✅ ngrok paid ($8/month)**
- Get permanent URL
- Point DreamHost domain to ngrok
- Very reliable
- Easy to demonstrate

**Cost:** $8/month | **Time to setup:** 10 minutes

### For ZERO Cloud Risk:
**✅ Run demo on your computer**
- Port forward from your router (port 3000)
- Share your public IP
- Judges can access it
- If they can't connect, use Zoom screen share

**Cost:** $0 | **Time to setup:** 0 minutes (if router configured)

---

## Bandwidth Cost Calculator

**Real example: Contest with 200 viewers over 4 hours**

1. **Static files (first load):** 200 × 500KB = 100MB
2. **API polling:** 200 viewers × (33KB every 10 seconds) = 24MB/min
3. **4 hours:** 24MB × 240 = 5.76GB
4. **Total:** ~6GB

**Cost breakdown:**
- ngrok free: ✅ FREE (with rate limits)
- ngrok paid: ✅ Included in $8/month
- Cloudflare Tunnel: ✅ FREE
- Tailscale: ✅ FREE
- VPS bandwidth: Most give 1-10TB free, so ✅ FREE

**Conclusion:** You won't pay extra for bandwidth with any of the free options!

---

## Security Reminder

⚠️ **Important:** Don't deploy your backend with API keys to DreamHost shared hosting. Use one of these solutions that keeps the backend on your machine or a secure VPS.

---

## Using Your Custom Domain (Namecheap + DreamHost)

### How It Works:
1. **Frontend Dashboard** → Deploy to DreamHost with your custom domain (`yourdomain.com`)
2. **Backend API** → Stays on your local machine
3. **Connection** → Frontend on DreamHost connects to backend via secure tunnel (ngrok/Cloudflare)

### Step-by-Step Setup:

#### 1. Get Your Domain
- Buy domain on Namecheap (e.g., `yourtradingbot.com`)
- Point it to DreamHost nameservers

#### 2. Deploy Frontend to DreamHost
```bash
cd dashboard
# Create production config pointing to your ngrok tunnel
echo "VITE_API_BASE_URL=https://your-ngrok-url.ngrok.io" > .env.production
npm run build
# Upload dist/ folder contents to DreamHost public_html
```

#### 3. Create Tunnel for Backend
```bash
# Start your backend
python dashboard_api/run_server.py

# In another terminal, start ngrok
ngrok http 8000

# Copy the https URL (e.g., https://abc123def456.ngrok.io)
```

#### 4. Update Frontend Config
Update `dashboard/.env.production` with your ngrok URL:
```bash
VITE_API_BASE_URL=https://abc123def456.ngrok.io
```

Then rebuild and re-upload to DreamHost:
```bash
npm run build
# Upload new dist/ folder to DreamHost
```

### Result:
- ✅ Dashboard accessible at: `https://yourdomain.com`
- ✅ Backend API runs on your computer
- ✅ API keys stay secure
- ✅ Custom domain looks professional

---

## Quick Start Commands

### Option A: ngrok (Easiest)
```bash
# Install ngrok
winget install ngrok

# Start your backend
python dashboard_api/run_server.py

# In another terminal, create tunnel
ngrok http 8000

# Copy the https URL (e.g., https://abc123.ngrok.io)
# Update dashboard/.env.production:
VITE_API_BASE_URL=https://abc123.ngrok.io

# Build and upload to DreamHost
cd dashboard
npm run build
# Upload dist/ folder contents to DreamHost
```

### Option B: Tailscale (Most Secure)
```bash
# Install Tailscale
winget install Tailscale.Tailscale

# Get your Tailscale IP (shown in Tailscale app)
# Update dashboard/.env.production:
VITE_API_BASE_URL=http://YOUR-TAILSCALE-IP:8000

# Build and upload to DreamHost
cd dashboard
npm run build
# Upload dist/ folder contents to DreamHost
```

### Option C: Just use your computer
```bash
# Configure router to forward port 3000 to your computer
# Find your public IP: whatismyipaddress.com
# Share: http://YOUR-PUBLIC-IP:3000
# Or use Zoom screen share for the demo
```

---

## Recommendation for Contest

**For contest judges:** Use **Option B (Tailscale)** OR **Zoom screen share**

**Why:**
1. Judges don't need to see it live on the internet
2. Screen share shows everything working perfectly
3. Zero risk of API keys being exposed
4. Zero cost

**If judges MUST see a live URL:** Use **ngrok paid ($8/month)** for the one month of the contest.

