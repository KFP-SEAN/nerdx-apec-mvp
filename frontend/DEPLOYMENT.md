# Deployment Guide - NERDX APEC Frontend

Complete guide for deploying the NERDX APEC frontend to production.

## Pre-Deployment Checklist

- [ ] All environment variables configured
- [ ] Backend API is deployed and accessible
- [ ] Stripe keys updated for production
- [ ] Domain/SSL certificate ready
- [ ] Build tested locally
- [ ] Error tracking configured
- [ ] Analytics setup (optional)

## Deployment Methods

### Method 1: Vercel (Recommended)

Vercel is the easiest way to deploy Next.js applications.

#### Steps:

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Login to Vercel**
```bash
vercel login
```

3. **Deploy**
```bash
vercel
```

4. **Set Environment Variables**
```bash
vercel env add NEXT_PUBLIC_API_URL production
vercel env add NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY production
```

5. **Deploy to Production**
```bash
vercel --prod
```

#### Vercel Configuration (vercel.json)
```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url",
    "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY": "@stripe-key"
  }
}
```

### Method 2: Docker + Cloud Provider

Deploy using Docker on AWS, GCP, Azure, or DigitalOcean.

#### Build Docker Image

```bash
# Build the image
docker build -t nerdx-apec-frontend:latest .

# Tag for registry
docker tag nerdx-apec-frontend:latest your-registry.com/nerdx-apec-frontend:latest

# Push to registry
docker push your-registry.com/nerdx-apec-frontend:latest
```

#### Run with Docker

```bash
docker run -d \
  --name nerdx-frontend \
  -p 80:3000 \
  -e NEXT_PUBLIC_API_URL=https://api.nerdx-apec.com \
  -e NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_xxx \
  --restart unless-stopped \
  nerdx-apec-frontend:latest
```

#### Docker Compose Production

```yaml
version: '3.8'

services:
  frontend:
    image: your-registry.com/nerdx-apec-frontend:latest
    ports:
      - "80:3000"
    environment:
      - NEXT_PUBLIC_API_URL=https://api.nerdx-apec.com
      - NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_xxx
      - NODE_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000/"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### Method 3: AWS EC2 + Docker

#### 1. Launch EC2 Instance
- Ubuntu 22.04 LTS
- t3.medium or larger
- Open ports: 80, 443, 22
- Configure security groups

#### 2. Connect and Setup
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 3. Deploy Application
```bash
# Clone repository
git clone https://github.com/your-org/nerdx-apec-mvp.git
cd nerdx-apec-mvp/frontend

# Create .env file
nano .env.production

# Build and run
docker-compose -f docker-compose.yml up -d
```

#### 4. Setup Nginx Reverse Proxy
```bash
# Install Nginx
sudo apt install nginx -y

# Configure Nginx
sudo nano /etc/nginx/sites-available/nerdx-apec
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/nerdx-apec /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. Setup SSL with Let's Encrypt
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Method 4: DigitalOcean App Platform

#### 1. Create App
- Go to DigitalOcean App Platform
- Create new app from GitHub repository
- Select `frontend` directory

#### 2. Configure Build
```yaml
name: nerdx-apec-frontend
services:
  - name: web
    github:
      repo: your-org/nerdx-apec-mvp
      branch: main
      deploy_on_push: true
    source_dir: /frontend
    build_command: npm run build
    run_command: npm run start
    environment_slug: node-js
    instance_count: 2
    instance_size_slug: basic-xs
    routes:
      - path: /
    envs:
      - key: NEXT_PUBLIC_API_URL
        value: https://api.nerdx-apec.com
      - key: NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
        value: pk_live_xxx
        type: SECRET
```

### Method 5: Kubernetes (Advanced)

#### Kubernetes Deployment (k8s/deployment.yaml)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nerdx-frontend
  labels:
    app: nerdx-frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nerdx-frontend
  template:
    metadata:
      labels:
        app: nerdx-frontend
    spec:
      containers:
      - name: frontend
        image: your-registry.com/nerdx-apec-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.nerdx-apec.com"
        - name: NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
          valueFrom:
            secretKeyRef:
              name: stripe-secret
              key: publishable-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: nerdx-frontend-service
spec:
  selector:
    app: nerdx-frontend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3000
  type: LoadBalancer
```

#### Deploy to Kubernetes
```bash
# Apply deployment
kubectl apply -f k8s/deployment.yaml

# Check status
kubectl get pods
kubectl get services

# Scale replicas
kubectl scale deployment nerdx-frontend --replicas=5
```

## Environment Variables

### Production Environment (.env.production)
```env
# API Configuration
NEXT_PUBLIC_API_URL=https://api.nerdx-apec.com

# Stripe Configuration (PRODUCTION KEYS!)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_xxx

# Analytics (Optional)
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX

# Environment
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
```

### Security Best Practices
1. **Never commit .env files** to version control
2. **Use secrets management** (AWS Secrets Manager, HashiCorp Vault)
3. **Rotate keys regularly**
4. **Use different keys** for dev/staging/production
5. **Enable HTTPS only**

## Performance Optimization

### 1. Enable CDN
```javascript
// next.config.js
module.exports = {
  assetPrefix: 'https://cdn.nerdx-apec.com',
}
```

### 2. Enable Compression
Already enabled in Next.js, but for Nginx:
```nginx
gzip on;
gzip_vary on;
gzip_min_length 256;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;
```

### 3. Cache Static Assets
```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Monitoring & Logging

### 1. Setup Sentry (Error Tracking)
```bash
npm install @sentry/nextjs
```

```javascript
// sentry.config.js
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
});
```

### 2. Setup Google Analytics
```javascript
// app/layout.tsx
<Script
  src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`}
  strategy="afterInteractive"
/>
```

### 3. Application Monitoring
- Use Vercel Analytics (if on Vercel)
- New Relic for detailed monitoring
- Datadog for infrastructure monitoring
- CloudWatch (if on AWS)

## CI/CD Pipeline

### GitHub Actions (.github/workflows/deploy.yml)
```yaml
name: Deploy Frontend

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      working-directory: ./frontend
      run: npm ci

    - name: Type check
      working-directory: ./frontend
      run: npm run type-check

    - name: Lint
      working-directory: ./frontend
      run: npm run lint

    - name: Build
      working-directory: ./frontend
      run: npm run build
      env:
        NEXT_PUBLIC_API_URL: ${{ secrets.API_URL }}
        NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: ${{ secrets.STRIPE_KEY }}

    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v20
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.ORG_ID }}
        vercel-project-id: ${{ secrets.PROJECT_ID }}
        vercel-args: '--prod'
        working-directory: ./frontend
```

## Rollback Strategy

### Vercel Rollback
```bash
# List deployments
vercel ls

# Rollback to previous deployment
vercel rollback [deployment-url]
```

### Docker Rollback
```bash
# Tag current as backup
docker tag nerdx-frontend:latest nerdx-frontend:backup

# Pull previous version
docker pull your-registry.com/nerdx-frontend:previous-tag

# Update and restart
docker-compose down
docker-compose up -d
```

### Kubernetes Rollback
```bash
# Rollback to previous revision
kubectl rollout undo deployment/nerdx-frontend

# Rollback to specific revision
kubectl rollout undo deployment/nerdx-frontend --to-revision=2
```

## Post-Deployment

### 1. Health Checks
```bash
# Test homepage
curl https://nerdx-apec.com

# Test API connectivity
curl https://nerdx-apec.com/api/health

# Check SSL
curl -vI https://nerdx-apec.com 2>&1 | grep SSL
```

### 2. Performance Testing
```bash
# Run Lighthouse
npx lighthouse https://nerdx-apec.com --view

# Load testing with Apache Bench
ab -n 1000 -c 10 https://nerdx-apec.com/
```

### 3. Monitor Logs
```bash
# Docker logs
docker logs -f nerdx-frontend

# Kubernetes logs
kubectl logs -f deployment/nerdx-frontend

# Nginx logs
tail -f /var/log/nginx/access.log
```

## Troubleshooting

### Build Fails
```bash
# Clear Next.js cache
rm -rf .next

# Clear node modules
rm -rf node_modules package-lock.json
npm install
```

### 502 Bad Gateway
- Check if container is running: `docker ps`
- Check container logs: `docker logs nerdx-frontend`
- Verify port mapping
- Check Nginx configuration

### Slow Performance
- Enable CDN
- Check database queries
- Enable caching
- Optimize images
- Review bundle size: `npm run build -- --analyze`

## Maintenance

### Regular Updates
```bash
# Update dependencies monthly
npm update
npm audit fix

# Update Docker base image
docker pull node:18-alpine
```

### Backup Strategy
- Backup environment variables
- Backup custom configurations
- Document all deployment steps
- Keep deployment history

## Cost Optimization

### Vercel
- Free tier: Good for testing
- Pro: $20/month (recommended)
- Enterprise: Custom pricing

### AWS
- t3.medium EC2: ~$30/month
- ECS Fargate: ~$40/month
- Load Balancer: ~$20/month

### DigitalOcean
- App Platform: $12-24/month
- Droplet + Spaces: $15-30/month

## Support

For deployment issues:
- Email: devops@nerdx-apec.com
- Slack: #deployment channel
- Documentation: See README.md

---

**Last Updated**: 2025-10-10
**Maintained By**: NERDX DevOps Team
