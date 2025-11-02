# Dashboard Deployment Guide

## Security First: Keep API Keys Safe

Your API keys are stored in `.env` on your local machine and **never** leave your machine. Only the dashboard frontend (which displays data) goes on the web.

## How It Works

1. **Backend API** (runs on your local machine on port 8000)
   - Has access to Aster API keys
   - Fetches account data, trades, positions
   - **Never deploy this to the cloud**

2. **Trading Bots** (run on your local machine)
   - Make trading decisions
   - Execute trades using API keys
   - **Never deploy to the cloud**

3. **Dashboard Frontend** (deploy to DreamHost)
   - Just displays data from the backend
   - No access to API keys
   - Safe to host publicly

## Deployment Steps

### Option 1: Use ngrok (Easiest)

#### Step 1: Install ngrok
```bash
# Download from https://ngrok.com/download
# Or use: npm install -g ngrok
```

#### Step 2: Create ngrok tunnel
```bash
ngrok http 8000
```
This gives you a URL like: `https://abc123def456.ngrok.io`

#### Step 3: Build dashboard with the ngrok URL
Create a file `dashboard/.env.production`:
```bash
VITE_API_BASE_URL=https://abc123def456.ngrok.io
```

#### Step 4: Build the dashboard
```bash
cd dashboard
npm run build
```
This creates a `dist` folder with static files.

#### Step 5: Deploy to DreamHost
1. Upload the `dist` folder contents to DreamHost
2. Place them in your `public_html` directory
3. Access your dashboard at `https://yourdomain.com`

#### Step 6: Keep ngrok running
ngrok will stop if you close the terminal. You can:
- Keep it running in a separate terminal
- Or use a paid ngrok account for persistent URLs

### Option 2: Use DreamHost with SSH (More Permanent)

If your DreamHost account supports SSH:

#### Step 1: Install Cloudflare Tunnel (Alternative to ngrok)
```bash
# More permanent solution
cloudflared tunnel create my-tunnel
cloudflared tunnel route dns my-tunnel yourdomain.com
cloudflared tunnel run my-tunnel
```

#### Step 2-5: Same as Option 1, but use the Cloudflare tunnel URL

### Option 3: Run everything on DreamHost (NOT RECOMMENDED)

⚠️ **Warning**: This exposes your API keys to a public server.

**Only do this if:**
- You use a Virtual Private Server (VPS) that you completely control
- You're comfortable with server security
- You understand the risks

For DreamHost shared hosting, this is **not recommended**.

## Environment Variables

### Development (already working)
Uses Vite proxy in `vite.config.js` to connect to `http://10.5.0.2:8000`

### Production (for deployment)
Create `dashboard/.env.production`:
```bash
# When using ngrok
VITE_API_BASE_URL=https://abc123def456.ngrok.io

# When using Cloudflare Tunnel
VITE_API_BASE_URL=https://yourdomain.com/tunnel
```

## Security Checklist

- ✅ API keys stay on your local machine
- ✅ Backend API never deployed to cloud
- ✅ Dashboard frontend is read-only
- ✅ All API calls go through secure tunnel (ngrok/Cloudflare)
- ✅ HTTPS encryption for all traffic

## Troubleshooting

### "Dashboard shows but no data"
- Check if ngrok is running: `ngrok http 8000`
- Update `.env.production` with correct ngrok URL
- Rebuild: `npm run build`

### "CORS errors"
- Backend already has CORS enabled
- If still issues, check ngrok URL is accessible

### "API timeout"
- Make sure backend is running on your local machine
- Check ngrok tunnel is active

## Future: Better Solution

For a production setup, consider:
1. **VPS on DigitalOcean/AWS** ($5-10/month)
2. **Reverse proxy with Nginx**
3. **HTTPS with Let's Encrypt**
4. **Port forwarding** from your router
5. **SSL certificates** for proper encryption

But for now, **ngrok is the safest and easiest option** to test with DreamHost.




