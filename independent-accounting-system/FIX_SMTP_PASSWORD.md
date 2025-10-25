# SMTP Password Fix - Immediate Action Required

## Problem Summary

✅ **Local SMTP test PASSED** - Password `cbkzetdulcsidlxp` works correctly
❌ **Railway SMTP test FAILED** - SMTP_PASSWORD environment variable is incorrect or missing

## Root Cause

Railway environment variable `SMTP_PASSWORD` is not set to the correct Gmail App Password.

## Solution: Update Railway Environment Variable (2 minutes)

### Method 1: Railway Web Dashboard (RECOMMENDED - 2 minutes)

**Step 1:** Open Railway Dashboard
```
https://railway.app/project/nerdx-accounting-system
```

**Step 2:** Click on your service (nerdx-apec-mvp or similar)

**Step 3:** Go to "Variables" tab

**Step 4:** Find or create `SMTP_PASSWORD` variable

**Step 5:** Set the value (copy/paste exactly):
```
cbkzetdulcsidlxp
```

**Step 6:** Save changes (Railway will auto-redeploy)

**Step 7:** Wait 2-3 minutes for deployment to complete

**Step 8:** Test email delivery:
```bash
curl -s -X POST "https://nerdx-apec-mvp-production.up.railway.app/api/v1/reports/daily/cell-5ca00d505e2b/send?report_date=2025-10-25" \
  -H "Content-Type: application/json" \
  -d '{"recipients":["sean@koreafnbpartners.com"]}'
```

### Method 2: Railway API (Alternative - for automation)

If Railway CLI is not linked, you can use the Railway GraphQL API directly:

**Step 1:** Get your Railway API token from https://railway.app/account/tokens

**Step 2:** Run this command (replace `YOUR_TOKEN` and `SERVICE_ID`):
```bash
curl -X POST https://backboard.railway.app/graphql/v2 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { variableUpsert(input: { projectId: \"PROJECT_ID\", serviceId: \"SERVICE_ID\", name: \"SMTP_PASSWORD\", value: \"cbkzetdulcsidlxp\" }) { id } }"
  }'
```

## Verification After Fix

### 1. Check Railway Logs
```bash
railway logs --limit 20
```

Look for successful email delivery logs.

### 2. Check PostgreSQL Logs
```python
# Run this locally (with DATABASE_URL set):
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://postgres:GRRydiOlZsvNALSMpDVkmtDJuhbVQbCS@ballast.proxy.rlwy.net:38243/railway')
cursor = conn.cursor()
cursor.execute('''
    SELECT generation_status, emails_sent, emails_failed, error_message
    FROM report_generation_logs
    ORDER BY execution_time DESC
    LIMIT 1
''')
row = cursor.fetchone()
print(f'Status: {row[0]}')
print(f'Emails Sent: {row[1]}')
print(f'Emails Failed: {row[2]}')
print(f'Error: {row[3] if row[3] else \"None\"}')
cursor.close()
conn.close()
"
```

### 3. Check Gmail Inbox
- Email: sean@koreafnbpartners.com
- Subject: `[Test Operations Cell] 일간 리포트 - 2025-10-25`
- Expected content: NERD12 revenue (1,500,000 KRW) and cost (600,000 KRW) data

## Expected Results After Fix

✅ Email delivery status: **success**
✅ Emails sent: **1**
✅ Emails failed: **0**
✅ Error message: **None**
✅ Gmail inbox: Email received with HTML daily report

## Timeline

- Fix application: **2 minutes** (set environment variable)
- Railway redeployment: **2-3 minutes** (automatic)
- Total time to resolution: **5 minutes**

## Why This Is The Shortest Path

1. **Local testing confirmed** the password works (test already passed)
2. **Only one environment variable** needs to be updated
3. **Railway auto-redeploys** when variables change (no manual deployment needed)
4. **No code changes** required
5. **No database changes** required

This is the **fundamental fix** - updating the environment variable to match the working local configuration.

---

**Created:** 2025-10-26
**Status:** Ready for immediate execution
**Action Required:** Update SMTP_PASSWORD in Railway Dashboard
