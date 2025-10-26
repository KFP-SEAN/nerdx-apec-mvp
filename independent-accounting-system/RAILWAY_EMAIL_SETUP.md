# Railway Email Setup Guide - Resend API

**IMPORTANT: Railway blocks SMTP ports (25, 587, 465)**
You MUST use HTTP-based email APIs like Resend, SendGrid, or Postmark.

This system uses **Resend API** for email delivery, which is Railway-compatible and easy to integrate.

---

## Why Resend?

✅ **Railway Compatible** - Uses HTTP API, not SMTP
✅ **Easy Integration** - Simple Python SDK
✅ **Free Tier** - 3,000 emails/month free
✅ **Fast Setup** - Domain verification in minutes
✅ **Great Developer Experience** - Clean API, good docs

---

## Setup Instructions

### Step 1: Create Resend Account

1. Go to [https://resend.com](https://resend.com)
2. Sign up for a free account
3. Verify your email address

### Step 2: Add and Verify Your Domain

1. Go to [Resend Domains](https://resend.com/domains)
2. Click "Add Domain"
3. Enter your domain (e.g., `yourdomain.com`)
4. Add the DNS records shown to your domain provider:
   - **SPF Record** (TXT): `v=spf1 include:resend.com ~all`
   - **DKIM Records** (TXT): Provided by Resend
   - **DMARC Record** (TXT): Optional but recommended

**DNS Record Example:**
```
Type: TXT
Name: @
Value: v=spf1 include:resend.com ~all

Type: TXT
Name: resend._domainkey
Value: [provided by Resend]
```

5. Wait for DNS propagation (usually 5-30 minutes)
6. Click "Verify Domain" in Resend dashboard

**Note:** For testing, you can use Resend's test domain, but for production, you should verify your own domain.

### Step 3: Get API Key

1. Go to [Resend API Keys](https://resend.com/api-keys)
2. Click "Create API Key"
3. Name it (e.g., "NERDX Railway Production")
4. Select permissions:
   - ✅ Sending access
   - ✅ Domain access (optional)
5. Copy the API key (starts with `re_`)

**IMPORTANT:** Save this key immediately - you won't be able to see it again!

### Step 4: Configure Railway Environment Variables

#### Option A: Railway Web Dashboard (Recommended)

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Open your project: `nerdx-accounting-system`
3. Click on your service
4. Go to "Variables" tab
5. Add/Update these variables:

```bash
RESEND_API_KEY=re_your_actual_api_key_here
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

6. Click "Save"
7. Railway will automatically redeploy your service

#### Option B: Railway CLI

```bash
# Set Resend API key
railway variables --set RESEND_API_KEY="re_your_actual_api_key_here"

# Set from email
railway variables --set SMTP_FROM_EMAIL="noreply@yourdomain.com"
```

### Step 5: Verify Configuration

After deploying, check the Railway logs to verify email configuration:

```bash
railway logs
```

Look for these log entries:
```
[Resend] API Key configured: True
[Resend] From: noreply@yourdomain.com
```

---

## Testing Email Sending

### Local Testing

1. Set environment variables in `.env` file:
```bash
RESEND_API_KEY=re_your_api_key_here
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

2. Run the test script:
```bash
python test_email.py your_email@example.com
```

3. Check your inbox for test emails

### Production Testing (Railway)

1. SSH into Railway container:
```bash
railway run bash
```

2. Run test script:
```bash
python test_email.py your_email@example.com
```

3. Check Railway logs for email sending status:
```bash
railway logs --filter "Resend"
```

### API Testing

You can also test via the API endpoint:

```bash
curl -X POST https://your-railway-app.railway.app/api/test-email \
  -H "Content-Type: application/json" \
  -d '{"email": "your_email@example.com"}'
```

---

## Troubleshooting

### Problem: "Resend API key not configured"

**Solution:**
1. Check that `RESEND_API_KEY` is set in Railway variables
2. Verify the key starts with `re_`
3. Ensure there are no extra spaces in the key
4. Redeploy the service after setting variables

### Problem: "Domain not verified"

**Solution:**
1. Go to [Resend Domains](https://resend.com/domains)
2. Check domain verification status
3. Verify all DNS records are correctly added
4. Wait for DNS propagation (use [DNS Checker](https://dnschecker.org))
5. Click "Verify Domain" again

### Problem: Email sent but not received

**Solution:**
1. Check spam folder
2. Verify sender domain is correct
3. Check Resend logs at [https://resend.com/emails](https://resend.com/emails)
4. Verify SPF/DKIM records are set up correctly
5. Check recipient email is valid

### Problem: "Rate limit exceeded"

**Solution:**
- Free tier: 3,000 emails/month, 100 emails/day
- Upgrade to paid plan if needed
- Check for email loops or excessive sending

### Problem: Railway logs show "Connection refused"

**Solution:**
- This usually means SMTP is being used instead of Resend API
- Verify `resend` package is installed in `requirements.txt`
- Check that `email_service.py` is using Resend API, not SMTP
- Ensure `resend.api_key` is being set correctly

---

## Email Service Architecture

### Current Implementation

The system uses **Resend API** (HTTP-based), not SMTP:

```
Application → Resend Python SDK → Resend API → Email Delivery
```

**File:** `services/email_sender/email_service.py`

```python
import resend
from config import settings

class EmailService:
    def __init__(self):
        resend.api_key = settings.resend_api_key

    async def send_email(self, to_email, subject, html_body):
        response = resend.Emails.send({
            "from": settings.smtp_from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_body
        })
        return True
```

### Why Not SMTP?

Railway blocks SMTP ports for security and anti-spam reasons:
- ❌ Port 25 (SMTP) - Blocked
- ❌ Port 587 (SMTP TLS) - Blocked
- ❌ Port 465 (SMTP SSL) - Blocked

HTTP APIs are the recommended approach:
- ✅ Port 443 (HTTPS) - Always open
- ✅ More reliable and scalable
- ✅ Better error handling and logging

---

## Railway Environment Variables

### Required Variables

```bash
# Email - Resend API
RESEND_API_KEY=re_your_api_key_here
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

### Optional Variables (Legacy SMTP - Not Used on Railway)

```bash
# These are kept for local development fallback
# DO NOT USE ON RAILWAY - SMTP is blocked!
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_password
SMTP_USE_TLS=True
```

---

## Migration from SMTP to Resend

If you were previously using SMTP (Gmail, etc.), here's what changed:

### Before (SMTP - Doesn't work on Railway)
```python
import smtplib
from email.mime.text import MIMEText

smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.starttls()
smtp.login(username, password)
smtp.send_message(msg)
```

### After (Resend API - Works on Railway)
```python
import resend

resend.api_key = "re_your_key"
resend.Emails.send({
    "from": "noreply@yourdomain.com",
    "to": ["recipient@example.com"],
    "subject": "Hello",
    "html": "<h1>Hello World</h1>"
})
```

### Environment Variables Changes

**Remove these (SMTP won't work on Railway):**
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`

**Add these instead:**
- `RESEND_API_KEY`
- `SMTP_FROM_EMAIL` (kept for compatibility, used as "from" address)

---

## Cost Comparison

### Resend Pricing

**Free Tier:**
- 3,000 emails/month
- 100 emails/day
- All features included
- Perfect for small projects

**Paid Plans:**
- $20/month - 50,000 emails
- $80/month - 100,000 emails
- Custom pricing for higher volumes

### Alternatives (Also Railway-Compatible)

1. **SendGrid**
   - Free: 100 emails/day
   - $19.95/month: 50,000 emails

2. **Postmark**
   - $15/month: 10,000 emails
   - Better deliverability

3. **AWS SES**
   - $0.10 per 1,000 emails
   - Requires more setup

**Recommendation:** Stick with Resend for simplicity and Railway compatibility.

---

## Monitoring Email Delivery

### Resend Dashboard

1. Go to [Resend Emails](https://resend.com/emails)
2. View all sent emails
3. Check delivery status
4. View bounce/complaint rates

### Railway Logs

Monitor email sending in real-time:

```bash
railway logs --filter "Resend"
```

Look for:
- ✅ `[Resend] ✅ Email sent successfully`
- ❌ `[Resend] ❌ Resend API Error`

### Application Logs

The email service logs detailed information:
- Configuration check (API key present)
- Email sending attempts
- Resend API responses
- Error details with stack traces

---

## Security Best Practices

### API Key Security

1. ✅ **Never commit API keys to Git**
2. ✅ **Use Railway environment variables**
3. ✅ **Rotate keys periodically**
4. ✅ **Use separate keys for dev/prod**
5. ❌ **Never log API keys**

### Email Security

1. ✅ **Verify domain with SPF/DKIM**
2. ✅ **Use dedicated sender domain**
3. ✅ **Implement rate limiting**
4. ✅ **Validate recipient emails**
5. ✅ **Monitor for bounces/complaints**

---

## FAQ

**Q: Can I use Gmail SMTP on Railway?**
A: No, Railway blocks SMTP ports. Use Resend API instead.

**Q: Do I need to verify my domain?**
A: For production, yes. For testing, you can use Resend's test domain.

**Q: How long does DNS propagation take?**
A: Usually 5-30 minutes, but can take up to 48 hours.

**Q: Can I send from any email address?**
A: No, you can only send from verified domains in Resend.

**Q: What if I exceed the free tier limit?**
A: Resend will queue emails until next month or you can upgrade.

**Q: Is Resend GDPR compliant?**
A: Yes, Resend is GDPR compliant and follows email best practices.

---

## Support

- **Resend Documentation:** https://resend.com/docs
- **Railway Documentation:** https://docs.railway.app
- **Email Service Code:** `services/email_sender/email_service.py`
- **Configuration:** `config.py`

---

## Summary Checklist

Before deploying to Railway, ensure:

- [ ] Resend account created
- [ ] Domain added and verified in Resend
- [ ] API key generated from Resend dashboard
- [ ] `RESEND_API_KEY` set in Railway variables
- [ ] `SMTP_FROM_EMAIL` set in Railway variables
- [ ] Test email sent successfully
- [ ] Railway logs show successful email sending
- [ ] Production emails received correctly

---

**Last Updated:** 2025-10-27
**System:** NERDX Independent Accounting System
**Email Service:** Resend API v0.8.0
