# Railway Email Quick Start - Resend API

**Problem:** Railway blocks SMTP ports (25, 587, 465)
**Solution:** Use Resend API (HTTP-based email service)

---

## 5-Minute Setup

### Step 1: Get Resend API Key (2 minutes)

1. Go to https://resend.com and sign up
2. Go to https://resend.com/api-keys
3. Click "Create API Key"
4. Copy the key (starts with `re_`)

### Step 2: Set Railway Variables (1 minute)

Go to Railway Dashboard → Your Service → Variables:

```bash
RESEND_API_KEY=re_your_actual_key_here
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

Click "Save" - Railway will auto-redeploy.

### Step 3: Test Email (1 minute)

After deployment completes, check logs:

```bash
railway logs --filter "Resend"
```

You should see:
```
[Resend] API Key configured: True
[Resend] From: noreply@yourdomain.com
```

### Step 4: Verify Domain (Optional - for production)

For testing, you can use Resend's test domain. For production:

1. Go to https://resend.com/domains
2. Click "Add Domain"
3. Add DNS records to your domain provider
4. Wait 5-30 minutes for DNS propagation
5. Click "Verify Domain"

---

## Test Email Sending

### Option A: Via Test Script (Recommended)

```bash
# SSH into Railway container
railway run bash

# Run test
python test_email.py your_email@example.com
```

### Option B: Via API

```bash
curl -X POST https://your-app.railway.app/api/test-email \
  -H "Content-Type: application/json" \
  -d '{"email": "your_email@example.com"}'
```

---

## Troubleshooting

### "Resend API key not configured"
- Check Railway variables are set
- Redeploy service after setting variables

### "Domain not verified"
- For testing: Use any email (Resend test domain)
- For production: Verify domain in Resend dashboard

### Email not received
- Check spam folder
- View logs: https://resend.com/emails
- Verify domain has SPF/DKIM records

---

## What Changed from SMTP?

**Before (doesn't work on Railway):**
```python
smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.send_message(msg)  # ❌ Connection refused
```

**After (works on Railway):**
```python
resend.api_key = "re_..."
resend.Emails.send({...})  # ✅ Works!
```

---

## Full Documentation

See [RAILWAY_EMAIL_SETUP.md](./RAILWAY_EMAIL_SETUP.md) for:
- Detailed setup instructions
- Domain verification guide
- DNS configuration examples
- Security best practices
- Cost comparison
- Advanced troubleshooting

---

## Summary Checklist

- [ ] Resend account created
- [ ] API key generated
- [ ] Railway variables set (`RESEND_API_KEY`, `SMTP_FROM_EMAIL`)
- [ ] Service redeployed
- [ ] Logs show "API Key configured: True"
- [ ] Test email sent successfully
- [ ] (Optional) Domain verified for production

---

**Need help?** See [RAILWAY_EMAIL_SETUP.md](./RAILWAY_EMAIL_SETUP.md)
