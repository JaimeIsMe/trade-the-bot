# Configure Public Hostname

## ✅ Success!
The cloudflared service is installed and running!

---

## 🎯 Next Step: Configure Public Hostname

Go back to your Cloudflare Zero Trust dashboard and configure the public hostname.

### In Cloudflare Dashboard:

1. **Click the blue "Next" button** at the bottom of the page

2. **You should now see a "Routes" page**

3. **Add a public hostname:**
   - Look for a section about adding a hostname or application
   - Or click **"Routes"** in the left sidebar
   - Click **"Add a public hostname"** or **"Add an application"**

4. **Configure it:**
   - **Subdomain:** `api` (or you can leave blank for root domain)
   - **Domain:** `tradethebot.com`
   - **Service type:** HTTP
   - **Service URL:** `http://localhost:8000`

5. **Save**

---

## What This Does:

This connects `api.tradethebot.com` (or `tradethebot.com`) → your backend on `localhost:8000`

Once this is configured, your dashboard will be able to connect to your backend API!

---

**Click "Next" in the Cloudflare dashboard and tell me what you see!**




