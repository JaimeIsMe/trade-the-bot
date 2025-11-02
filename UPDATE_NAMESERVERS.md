# Update Nameservers in Namecheap

## ✅ What You Have:
Cloudflare gave you TWO nameservers:
1. `leif.ns.cloudflare.com`
2. `sierra.ns.cloudflare.com`

**Copy these down!** (Or use the "Click to copy" buttons next to them)

---

## 📋 Step-by-Step Instructions:

### Step 1: Open Namecheap in a New Tab
1. Keep this Cloudflare tab open (so you can see the nameservers)
2. Open a new tab
3. Go to [namecheap.com](https://namecheap.com)
4. Log into your account

### Step 2: Go to Domain List
1. Click "Domain List" in the top menu
2. Find `tradethebot.com`
3. Click "Manage" next to it

### Step 3: Find Nameservers Section
1. Look for "Nameservers" section
2. You should see something like:
   - Current nameservers showing `dns1.registrar-servers.com` and `dns2.registrar-servers.com`

### Step 4: Update Nameservers
1. Click "Change" or "Custom DNS" (depending on what you see)
2. Select "Custom DNS" option
3. Delete the old nameservers:
   - Remove: `dns1.registrar-servers.com`
   - Remove: `dns2.registrar-servers.com`
4. Add the Cloudflare nameservers:
   - Add: `leif.ns.cloudflare.com`
   - Add: `sierra.ns.cloudflare.com`
5. **Save** or **Submit** changes

### Step 5: Optional - Check DNSSEC
- Cloudflare says to turn off DNSSEC in Namecheap
- Look for "DNSSEC" setting and turn it OFF if it's on
- (You can turn it back on later through Cloudflare)

---

## ⏳ After You Save:

1. Go back to Cloudflare tab
2. Cloudflare will detect the change (can take 5 minutes to 24 hours)
3. You'll get an email when it's active
4. Cloudflare says it usually happens quickly!

---

## 🚨 Important:
- **Don't worry about downtime** - Cloudflare says this is unlikely
- **These nameservers are YOUR unique ones** - don't share them publicly
- **Keep the Cloudflare tab open** so you can reference the nameservers

---

**Go ahead and update the nameservers in Namecheap, then come back and tell me when you've saved the changes!**




