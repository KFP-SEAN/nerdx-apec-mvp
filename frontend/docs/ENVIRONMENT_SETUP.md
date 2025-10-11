# Environment Variables Setup

## Required Variables

### Frontend (.env.local)
```bash
NEXT_PUBLIC_SHOPIFY_DOMAIN=your-store.myshopify.com
NEXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN=your_storefront_token
NEXT_PUBLIC_SHOPIFY_APP_URL=http://localhost:3001
NODE_ENV=production
```

### Backend (.env)
```bash
SHOPIFY_ADMIN_API_TOKEN=your_admin_token
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
REDIS_URL=redis://localhost:6379
JWT_SECRET=your_jwt_secret
```

## Deployment Platforms

### Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Login: `vercel login`
3. Deploy: `vercel --prod`
4. Add environment variables in Vercel dashboard

### AWS / Docker
1. Build image: `docker build -t nerdx-apec .`
2. Run: `docker run -p 3000:3000 -e NEXT_PUBLIC_SHOPIFY_DOMAIN=... nerdx-apec`

### Domain Setup
1. Point domain to Vercel/AWS
2. Configure SSL (auto with Vercel)
3. Update Shopify app URLs

## Monitoring

### Sentry (Error Tracking)
```bash
NEXT_PUBLIC_SENTRY_DSN=your_sentry_dsn
SENTRY_AUTH_TOKEN=your_auth_token
```

### Google Analytics
```bash
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```
