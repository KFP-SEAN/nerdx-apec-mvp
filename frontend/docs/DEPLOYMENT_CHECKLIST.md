# Production Deployment Checklist

## Pre-Deployment

- [ ] All tests passing (90%+ success rate)
- [ ] No console errors in production build
- [ ] Environment variables documented
- [ ] Database backups configured
- [ ] Monitoring setup (Sentry, Analytics)

## Vercel Deployment

- [ ] Install Vercel CLI: `npm i -g vercel`
- [ ] Login to Vercel: `vercel login`
- [ ] Link project: `vercel link`
- [ ] Add environment variables in dashboard
- [ ] Deploy preview: `vercel`
- [ ] Test preview deployment
- [ ] Deploy production: `vercel --prod`

## Post-Deployment

- [ ] Verify all pages load
- [ ] Test product browsing
- [ ] Test cart functionality
- [ ] Test checkout flow
- [ ] Check Shopify webhook delivery
- [ ] Monitor error rates
- [ ] Set up domain (if applicable)
- [ ] Configure SSL/HTTPS
- [ ] Update Shopify app URLs

## Domain Configuration

1. Add custom domain in Vercel dashboard
2. Configure DNS records:
   - Type: CNAME
   - Name: www (or @)
   - Value: cname.vercel-dns.com
3. Wait for DNS propagation (up to 48h)
4. Enable automatic HTTPS

## Monitoring Setup

### Sentry
```bash
npm install @sentry/nextjs
npx @sentry/wizard@latest -i nextjs
```

### Google Analytics
Add GA script to `app/layout.tsx`

## Rollback Plan

If issues occur:
1. `vercel rollback` to previous deployment
2. Check error logs: `vercel logs`
3. Fix issues locally
4. Re-deploy after testing

## Performance Checklist

- [ ] Lighthouse score > 90
- [ ] First Contentful Paint < 1.5s
- [ ] Time to Interactive < 3s
- [ ] Images optimized (WebP/AVIF)
- [ ] Code splitting enabled
- [ ] CDN configured

## Security Checklist

- [ ] HTTPS enabled
- [ ] Environment vars secure
- [ ] No API keys in frontend code
- [ ] CORS configured
- [ ] Rate limiting enabled
- [ ] XSS protection enabled
