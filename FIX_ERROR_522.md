# Fix Error 522 - Connection Timed Out

## 🔍 What's Wrong:

**Error 522:** Cloudflare can't connect to the origin server (DreamHost)

The issue: Your DNS is pointing to Cloudflare nameservers, but Cloudflare doesn't know where to find DreamHost.

---

## 🛠️ Solution: Configure DNS in Cloudflare

We need to add DNS records in Cloudflare to point to DreamHost.

### Step 1: Get DreamHost IP Address

In your DreamHost panel, find the IP address for `tradethebot.com`. It should be listed in your hosting settings.

**Or** we can check what IP DreamHost assigned:

Let me help you find it...

### Step 2: Add DNS Records in Cloudflare

1. Go to Cloudflare dashboard
2. Click on `tradethebot.com` domain
3. Click **"DNS"** in the top menu
4. Add these records:

**A Record:**
- **Type:** A
- **Name:** @ (root domain)
- **Content:** [DreamHost IP address]
- **Proxy status:** Proxied (orange cloud)

**CNAME Record (for www):**
- **Type:** CNAME
- **Name:** www
- **Content:** tradethebot.com
- **Proxy status:** Proxied (orange cloud)

---

## 🎯 Quick Fix: Let me help you find the DreamHost IP

Can you go to your DreamHost dashboard and look for the IP address assigned to `tradethebot.com`?

It's usually shown in the domain/hosting section.

**Tell me the IP address and I'll guide you through adding it to Cloudflare!**




