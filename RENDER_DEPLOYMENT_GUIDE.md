# 🚀 Render Deployment Guide - Elite Wealth Capital

## Option 1: Using Existing Service (Easiest)

Your current service is already working at **elitewealthcapita.uk**!

Just add the 3 missing Cloudinary variables:

1. Go to: https://dashboard.render.com/web/srv-d72cbd0ule4c73e27km0
2. Click "**Environment**" tab
3. Click "**Add Environment Variable**" (3 times)

```
CLOUDINARY_CLOUD_NAME = dh5ikf5un
CLOUDINARY_API_KEY = 926391542761186
CLOUDINARY_API_SECRET = RGBNIYy2_c_wybiwH7-qINfbF5M
```

4. Click "**Save Changes**"
5. Wait 3 minutes for redeploy
6. ✅ Done!

---

## Option 2: Create NEW Render Service (Fresh Start)

If you want to delete current workspace and start fresh:

### Step 1: Create New Web Service

1. Go to: https://dashboard.render.com
2. Click "**New +**" → "**Web Service**"
3. Connect GitHub: **AGWU662/MY-SITE**
4. Configure:

```
Name: elite-wealth-capital (or any name)
Region: Frankfurt (EU) or Oregon (US)
Branch: main
Runtime: Docker
Instance Type: Starter ($7/month) or Free
```

### Step 2: Add ALL Environment Variables

**Option A: Copy from file**
1. Open `render-production.env` file
2. Copy all variables (lines 19-56)
3. In Render → Environment tab
4. Click "Add Environment Variable" for each one
5. Paste Key and Value

**Option B: Bulk Import (if available)**
1. Click "Import from .env"
2. Upload `render-production.env`
3. Click Import

**Required Variables (26 total):**
```
SECRET_KEY=2b701cac9564763581c440415aae95ef
DEBUG=False
DJANGO_SETTINGS_MODULE=elite_wealth_capital.settings
ALLOWED_HOSTS=elitewealthcapita.uk,www.elitewealthcapita.uk,my-site-ghnp.onrender.com
DATABASE_URL=postgresql://elite_admin:4nByWZVjPEQ2G1uIIki0vSCn99fuxKmw@dpg-d72e1uh4tr6s73bdvfp0-a/elite_wealth_k85f
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.zoho.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=admin@elitewealthcapita.uk
EMAIL_HOST_PASSWORD=myfavour1$
DEFAULT_FROM_EMAIL=admin@elitewealthcapita.uk
ADMIN_EMAIL=admin@elitewealthcapita.uk
CLOUDINARY_CLOUD_NAME=dh5ikf5un
CLOUDINARY_API_KEY=926391542761186
CLOUDINARY_API_SECRET=RGBNIYy2_c_wybiwH7-qINfbF5M
COMPANY_NAME=Elite Wealth Capital
COMPANY_EMAIL=admin@elitewealthcapita.uk
COMPANY_ADDRESS=London, United Kingdom, Norway
COMPANY_WEBSITE=https://elitewealthcapita.uk
```

### Step 3: Configure Domain (elitewealthcapita.uk)

1. In Render → Click your new service
2. Go to "**Settings**" tab
3. Scroll to "**Custom Domains**"
4. Click "**Add Custom Domain**"
5. Enter: `elitewealthcapita.uk`
6. Click "**Add**"
7. Also add: `www.elitewealthcapita.uk`

### Step 4: Update DNS Records

**In your domain registrar (e.g., Namecheap, GoDaddy):**

**A Record (Root domain):**
```
Type: A
Name: @
Value: 216.24.57.1 (Render's IP)
TTL: Automatic
```

**CNAME Record (www subdomain):**
```
Type: CNAME
Name: www
Value: your-service-name.onrender.com
TTL: Automatic
```

**Wait:** DNS propagation takes 5-60 minutes

### Step 5: Verify Deployment

1. Wait for build to complete (3-5 minutes)
2. Check logs for errors
3. Visit: `https://elitewealthcapita.uk`
4. Test:
   - Login/signup works ✅
   - Profile image upload ✅
   - Dashboard loads ✅
   - Investments show ✅

---

## Option 3: Keep Current Service + Add Cloudinary (RECOMMENDED)

**Why?**
- Domain already configured
- Database already connected
- All users' data already there
- Just add 3 variables and done!

**Steps:**
1. Add Cloudinary variables (see Option 1)
2. Save and redeploy
3. ✅ Done in 5 minutes!

---

## What About Old Workspace?

**Safe to delete IF:**
- ✅ New service deployed successfully
- ✅ Domain pointing to new service
- ✅ Database URL same in both
- ✅ Site working on new service

**User data is SAFE because:**
- Database is separate service
- Not tied to web service
- Same DATABASE_URL = same data

**Steps to delete old service:**
1. Verify new service works
2. Go to old service settings
3. Scroll to "Danger Zone"
4. Click "Delete Service"
5. Confirm deletion

---

## 🎯 RECOMMENDATION

**Just add the 3 Cloudinary variables to your existing service!**

Your current setup is perfect:
- ✅ Domain working
- ✅ Database connected
- ✅ All environment variables set
- ✅ Users can create accounts

Only missing: **Cloudinary** (for image uploads)

**5 minutes to fix:**
1. Environment tab
2. Add 3 Cloudinary variables
3. Save
4. Wait for redeploy
5. ✅ Site fully working with image uploads!

No need to recreate everything! 🎉

---

## Files Reference

- `render-production.env` - All environment variables
- `CLOUDINARY_QUICK_START.md` - Cloudinary setup guide
- `DATA_PERSISTENCE_GUIDE.md` - Data safety explanation
- `.env.example` - Template for local development

---

## Need Help?

**Common Issues:**

1. **502 Bad Gateway** → Check logs for errors
2. **Static files not loading** → Run collectstatic in Shell
3. **Domain not working** → Check DNS records
4. **Images not uploading** → Add Cloudinary variables

**Render Dashboard:**
- Logs: Real-time application logs
- Shell: Access to container terminal
- Metrics: CPU, memory usage

**Support:**
- Render Docs: https://render.com/docs
- Django Docs: https://docs.djangoproject.com
