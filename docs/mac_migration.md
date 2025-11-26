# Migrating Aster Vibe Trader to macOS

This playbook walks through moving the trading stack (bots, API, dashboard, Cloudflare tunnel) from the current Windows box to a macOS host with minimal downtime.

## 1. Prep on Windows (no downtime)

1. **Freeze repo state**
   ```powershell
   cd C:\Users\papa\Documents\coding_projects\crypto\aster\aster_vibe_comp
   git status
   ```
   Commit/stash anything you want to keep before copying.

2. **Back up secrets**
   - `.env` (ASTER wallet keys, API keys, OpenAI/Qwen keys, etc.)
   - `cloudflared` credentials (if using a named tunnel): `C:\Users\papa\.cloudflared\cert.pem` plus any `*.json` tunnel credential files.
   - Any log/history you want (`logs/`, `data/`, etc.)

3. **Capture current config**
   - `config/config.py` is already tracked, but note any local overrides/environment variables.
   - Document the current Cloudflare tunnel name (`cloudflared tunnel list`).

4. **Plan cutover window**
   - Keep Windows bots running while you provision the Mac.
   - Downtime only occurs when you stop Windows bots and start Mac bots (goal: <5 minutes).

## 2. Set up the Mac host

> Commands assume macOS 14+ with [Homebrew](https://brew.sh/). Install Homebrew first if needed:
> `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

1. **Clone repo**
   ```bash
   git clone https://github.com/<your-account>/aster_vibe_comp.git
   cd aster_vibe_comp
   ```

2. **Install system dependencies**
   ```bash
   brew install python@3.11 node@18 cloudflared
   # optional but recommended
   brew install git wget
   ```
   Ensure the new Python is first in PATH (`brew info python@3.11` for the `echo` export line).

3. **Create virtual environment**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Install frontend deps**
   ```bash
   cd dashboard
   npm install
   cd ..
   ```

5. **Restore secrets**
   - Copy `.env` from Windows to the project root (use AirDrop, scp, or password manager).
   - Ensure file permissions restrict access: `chmod 600 .env`.

6. **Cloudflare tunnel**
   - Copy `cert.pem` (and the tunnel credential JSON if using named tunnels) to `~/.cloudflared/` on the Mac.
   - Or re-login: `cloudflared tunnel login`.
   - Confirm the tunnel appears: `cloudflared tunnel list`.

## 3. Dry-run on Mac (while Windows bots still live)

1. **Start backend/bots locally**
   ```bash
   source .venv/bin/activate
   python main_multi_bot.py
   ```
   - Verify API: `curl http://localhost:8000/api/bots`.
   - Check logs to ensure each bot runs without errors.

2. **Start Cloudflare tunnel (test)**
   ```bash
   cloudflared tunnel run tradethebot
   ```
   - Or use a temporary quick tunnel: `cloudflared tunnel --url http://localhost:8000`.
   - Verify `https://api.tradethebot.com/api/bots` returns data.
   - Once validated, stop both processes (`Ctrl+C`) so Windows can keep serving production until the official cutover.

## 4. Cutover plan

1. **Schedule <5 minute window.**
2. **Stop Windows services**
   ```powershell
   # on Windows host
   Stop-Process -Name python -Force
   Stop-Process -Name cloudflared -Force
   ```
3. **Start on Mac**
   ```bash
   source .venv/bin/activate
   python main_multi_bot.py > logs/mac_bots.log 2>&1 &
   cloudflared tunnel run tradethebot > logs/cloudflared.log 2>&1 &
   ```
4. **Verify**
   - `curl http://localhost:8000/api/bots`
   - `curl https://api.tradethebot.com/api/bots`
   - Dashboard at `https://tradethebot.com` should show live data again.

If any issue occurs, stop the Mac processes and restart the Windows bots/tunnel (rollback).

## 5. Post-migration housekeeping

- Update any monitoring scripts to point to the Mac host.
- Configure Mac launch agents (or `pm2`, `supervisord`, etc.) for auto-restart:
  - Example plist for bots: `~/Library/LaunchAgents/com.tradethebot.bots.plist`
  - Example plist for Cloudflare tunnel.
- Ensure backups cover the new host.
- Remove secrets from the old Windows machine if it will be decommissioned.

## 6. Notes & tips

- **Python version parity**: Stick with 3.11 to avoid dependency mismatches.
- **Permissions**: macOS enforces stricter permissions; `chmod` scripts/logs as needed.
- **Keychain vs .env**: You can migrate secrets into macOS Keychain and source them in `.zshrc` if preferred.
- **Zero-downtime option**: Run bots simultaneously on both machines but only expose one Cloudflare tunnel at a time (not recommended unless you ensure they don’t double-trade on the same wallet).
- **Testing**: Use `scripts/test_quick_trade.py` on the Mac to confirm trade execution before the cutover.

Following this checklist keeps downtime to the few minutes it takes to stop Windows and start the Mac processes. Let me know when you’re ready to execute and we can go through each step live.



