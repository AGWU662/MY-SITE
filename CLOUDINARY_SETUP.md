# Cloudinary Setup Guide

## Why Cloudinary?
Render uses **ephemeral filesystem** — uploaded files (profile images, KYC documents) are lost on restart/redeployment. Cloudinary provides permanent cloud storage.

## Setup Steps

### 1. Create Cloudinary Account
1. Go to [https://cloudinary.com/users/register/free](https://cloudinary.com/users/register/free)
2. Sign up for FREE account (25GB storage, 25GB bandwidth/month)
3. Verify your email

### 2. Get Your Credentials
After login, go to Dashboard:
- **Cloud Name**: `dxxxxxxxxxxxxx` (visible at top)
- **API Key**: Your API key (long number)
- **API Secret**: Your API secret (click "eye" icon to reveal)

### 3. Add to Render Environment Variables
In your Render dashboard → Service → Environment:

```
CLOUDINARY_CLOUD_NAME=your-cloud-name-here
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=your-api-secret-here
```

### 4. How It Works

**Profile Images**:
- User uploads profile photo
- Django saves to Cloudinary automatically
- Returns URL like: `https://res.cloudinary.com/your-cloud/image/upload/v123456/profiles/user123.jpg`
- Stored permanently, no data loss on redeploy

**KYC Documents**:
- Same process for ID cards, passports, etc.
- Secure storage with access control
- Fast CDN delivery worldwide

### 5. Local Development
In development (DEBUG=True), files save locally to `media/` folder as usual. Cloudinary only activates in production.

### 6. Folder Structure in Cloudinary
Your files will be organized:
```
/profiles/          → User profile images
/kyc/id_front/      → KYC ID front images
/kyc/id_back/       → KYC ID back images
/kyc/selfie/        → KYC selfie images
```

### 7. Admin Panel
Upload/view images directly in Django admin — everything works the same, but storage is in cloud.

## Free Tier Limits
- **Storage**: 25 GB
- **Bandwidth**: 25 GB/month
- **Transformations**: 25 credits/month
- **Images**: Unlimited

Perfect for investment platform with 1000s of users!

## Already Configured
✅ `cloudinary` and `django-cloudinary-storage` added to requirements.txt
✅ Settings configured to auto-switch in production
✅ All model ImageFields work automatically
✅ No code changes needed

Just add the 3 environment variables to Render and redeploy!
