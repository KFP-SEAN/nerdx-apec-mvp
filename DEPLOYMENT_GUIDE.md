# 🚀 Production 배포 가이드

## 📋 개요

NERDX APEC MVP를 Production 환경에 배포하기 위한 완전한 가이드입니다.

**예상 소요 시간**: 4-6시간
**필요 사항**: AWS/Vercel 계정, Shopify Store, 도메인

---

## 🏗️ 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                   (Next.js 14 - Vercel)                      │
│                  https://nerdx.com                           │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ├─── Shopify Storefront API
                  │    (제품, 체크아웃)
                  │
                  ├─── Shopify Checkout
                  │    (결제 처리)
                  │
                  └─── Custom Shopify App
                       (AR 액세스 관리)
                            │
                            ├─── Neo4j (Graph DB)
                            ├─── Redis (Idempotency)
                            └─── SMTP (Notifications)
```

---

## 1️⃣ Frontend 배포 (Vercel)

### Step 1: Vercel 프로젝트 생성

1. [Vercel Dashboard](https://vercel.com) 접속
2. **New Project** 클릭
3. GitHub Repository 연결
   - Repository: `nerdx-apec-mvp`
   - Root Directory: `frontend`
   - Framework Preset: Next.js

### Step 2: 환경 변수 설정

Vercel Dashboard → Settings → Environment Variables:

```env
# Shopify
NEXT_PUBLIC_SHOPIFY_DOMAIN=nerdx.myshopify.com
NEXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN=shpat_xxxxx

# Custom App
NEXT_PUBLIC_SHOPIFY_APP_URL=https://shopify-app.nerdx.com

# API
NEXT_PUBLIC_API_URL=https://api.nerdx.com

# Analytics (선택사항)
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

### Step 3: 빌드 설정

```json
// vercel.json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["icn1"]
}
```

### Step 4: 배포

```bash
# 로컬에서 테스트
cd frontend
npm run build
npm start

# Vercel 배포
vercel --prod
```

### Step 5: 도메인 설정

1. Vercel Dashboard → Settings → Domains
2. Custom Domain 추가: `nerdx.com`
3. DNS 설정:
   ```
   Type: CNAME
   Name: @
   Value: cname.vercel-dns.com
   ```
4. SSL 인증서 자동 발급 (Let's Encrypt)

---

## 2️⃣ Custom Shopify App 배포 (AWS/Heroku)

### Option A: AWS EC2

#### Step 1: EC2 인스턴스 생성

1. AWS Console → EC2 → Launch Instance
2. 설정:
   ```
   AMI: Ubuntu 22.04 LTS
   Instance Type: t3.small (2 vCPU, 2GB RAM)
   Storage: 20GB gp3
   Security Group:
     - Port 22 (SSH)
     - Port 443 (HTTPS)
     - Port 3001 (App)
   ```

#### Step 2: 서버 설정

```bash
# SSH 접속
ssh -i keypair.pem ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com

# Node.js 설치
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 프로젝트 클론
git clone https://github.com/your-org/nerdx-apec-mvp.git
cd nerdx-apec-mvp/shopify-custom-app

# 의존성 설치
npm install --production

# PM2 설치 (프로세스 관리)
sudo npm install -g pm2

# 환경 변수 설정
nano .env
```

#### Step 3: 환경 변수

```env
# Shopify
SHOPIFY_DOMAIN=nerdx.myshopify.com
SHOPIFY_ADMIN_API_TOKEN=shpat_admin_xxxxx
SHOPIFY_WEBHOOK_SECRET=xxxxx

# Neo4j
NEO4J_URI=bolt://neo4j.nerdx.com:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=xxxxx

# Redis
REDIS_URL=redis://redis.nerdx.com:6379

# JWT
JWT_SECRET=xxxxx (32+ characters)
JWT_PUBLIC_KEY=/path/to/public.pem
JWT_PRIVATE_KEY=/path/to/private.pem

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@nerdx.com
SMTP_PASSWORD=xxxxx

# App
NODE_ENV=production
PORT=3001
LOG_LEVEL=info
```

#### Step 4: PM2로 실행

```bash
# 앱 시작
pm2 start npm --name "shopify-app" -- start

# 자동 시작 설정
pm2 startup
pm2 save

# 로그 확인
pm2 logs shopify-app
```

#### Step 5: Nginx 리버스 프록시

```bash
# Nginx 설치
sudo apt-get install nginx

# 설정 파일
sudo nano /etc/nginx/sites-available/shopify-app
```

```nginx
server {
    listen 80;
    server_name shopify-app.nerdx.com;

    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# 설정 활성화
sudo ln -s /etc/nginx/sites-available/shopify-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# SSL 인증서 (Let's Encrypt)
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d shopify-app.nerdx.com
```

### Option B: Heroku (더 간단)

```bash
# Heroku CLI 설치
curl https://cli-assets.heroku.com/install.sh | sh

# 로그인
heroku login

# 앱 생성
cd shopify-custom-app
heroku create nerdx-shopify-app

# 환경 변수 설정
heroku config:set SHOPIFY_DOMAIN=nerdx.myshopify.com
heroku config:set NEO4J_URI=bolt://...
# ... (모든 환경 변수)

# 배포
git push heroku main

# 로그 확인
heroku logs --tail
```

---

## 3️⃣ Neo4j 배포

### Option A: Neo4j Aura (권장)

1. [Neo4j Aura](https://neo4j.com/cloud/aura/) 접속
2. **Create Database** 클릭
3. 설정:
   ```
   Region: Seoul (ap-northeast-2)
   Memory: 2GB
   Storage: 8GB
   ```
4. Connection URI 복사:
   ```
   bolt://xxxxx.databases.neo4j.io
   ```

### Option B: Self-Hosted (Docker)

```bash
# EC2에 Docker 설치
sudo apt-get install docker.io docker-compose

# docker-compose.yml
version: '3'
services:
  neo4j:
    image: neo4j:5.12
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/yourpassword
    volumes:
      - ./data:/data
      - ./logs:/logs
    restart: always
```

```bash
# 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f neo4j
```

---

## 4️⃣ Redis 배포

### Option A: AWS ElastiCache

1. AWS Console → ElastiCache → Create
2. 설정:
   ```
   Engine: Redis
   Node Type: cache.t3.micro
   Number of nodes: 1
   ```
3. Endpoint 복사:
   ```
   redis.xxxxx.cache.amazonaws.com:6379
   ```

### Option B: Redis Cloud

1. [Redis Cloud](https://redis.com/cloud/) 접속
2. Free tier 생성
3. Connection string 복사

---

## 5️⃣ Shopify Production Store 설정

### Step 1: Development → Production 전환

1. Shopify Admin → Settings → Plan
2. **Choose a plan** 클릭
3. 플랜 선택:
   - **Shopify Basic**: $29/month
   - **Shopify**: $79/month (권장)
   - **Advanced**: $299/month

### Step 2: Webhook 업데이트

1. Shopify Admin → Settings → Notifications → Webhooks
2. URL 업데이트:
   ```
   https://shopify-app.nerdx.com/webhooks/orders/paid
   https://shopify-app.nerdx.com/webhooks/orders/cancelled
   https://shopify-app.nerdx.com/webhooks/refunds/create
   ```

### Step 3: Custom App 권한 확인

1. Admin → Apps → Development apps
2. API credentials 확인
3. Production access token 사용

### Step 4: 결제 게이트웨이 설정

1. Admin → Settings → Payments
2. Shopify Payments 활성화 또는
3. Stripe/PayPal 연동

---

## 6️⃣ DNS 및 도메인 설정

### DNS 레코드

```
# Frontend (Vercel)
Type: CNAME
Name: @
Value: cname.vercel-dns.com

Type: CNAME
Name: www
Value: cname.vercel-dns.com

# Custom App (AWS)
Type: A
Name: shopify-app
Value: [EC2 IP Address]

# API (if separate)
Type: A
Name: api
Value: [API Server IP]
```

---

## 7️⃣ 모니터링 및 로깅

### Vercel Analytics

Vercel Dashboard → Analytics:
- Real-time traffic
- Core Web Vitals
- 사용자 지표

### Custom App Monitoring

**Prometheus + Grafana**:

```yaml
# docker-compose.yml에 추가
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

### 로그 관리

**Option 1: CloudWatch (AWS)**
```bash
# CloudWatch Logs Agent 설치
sudo apt-get install awslogs
```

**Option 2: Papertrail**
```bash
# PM2 logs를 Papertrail로 전송
pm2 install pm2-papertrail
pm2 set pm2-papertrail:host logs.papertrailapp.com
pm2 set pm2-papertrail:port 12345
```

---

## 8️⃣ 보안 설정

### SSL/TLS

- ✅ Vercel: 자동 SSL (Let's Encrypt)
- ✅ Custom App: Certbot 사용
- ✅ Neo4j Aura: TLS 기본 활성화

### 환경 변수 보안

```bash
# AWS Secrets Manager 사용 (권장)
aws secretsmanager create-secret \
  --name nerdx/shopify-app \
  --secret-string file://secrets.json
```

### 방화벽 설정

```bash
# UFW (Ubuntu Firewall)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Rate Limiting

Nginx에서 설정:
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

server {
    location /api/ {
        limit_req zone=api burst=20;
    }
}
```

---

## 9️⃣ 백업 및 복구

### Neo4j 백업

```bash
# 자동 백업 스크립트
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
neo4j-admin dump --database=neo4j --to=/backups/neo4j-$DATE.dump

# S3에 업로드
aws s3 cp /backups/neo4j-$DATE.dump s3://nerdx-backups/neo4j/
```

### 데이터베이스 복구

```bash
# 백업에서 복구
neo4j-admin load --from=/backups/neo4j-20251011.dump --database=neo4j --force
```

---

## 🔟 배포 체크리스트

### Pre-Deployment

- [ ] 모든 테스트 통과 확인
- [ ] 환경 변수 설정 완료
- [ ] SSL 인증서 준비
- [ ] 백업 전략 수립
- [ ] 모니터링 도구 설정

### Deployment

- [ ] Frontend Vercel 배포
- [ ] Custom App AWS/Heroku 배포
- [ ] Neo4j 데이터베이스 생성
- [ ] Redis 인스턴스 생성
- [ ] DNS 레코드 설정

### Post-Deployment

- [ ] Smoke Tests 실행
- [ ] 성능 테스트
- [ ] 보안 검토
- [ ] 모니터링 대시보드 확인
- [ ] 백업 테스트

---

## 📊 성능 최적화

### Frontend (Vercel)

```javascript
// next.config.js
module.exports = {
  images: {
    domains: ['cdn.shopify.com'],
    formats: ['image/avif', 'image/webp'],
  },
  compress: true,
  poweredByHeader: false,
}
```

### Custom App (Node.js)

```javascript
// 프로덕션 최적화
const compression = require('compression')
app.use(compression())

// Connection pooling
const neo4jDriver = neo4j.driver(uri, auth, {
  maxConnectionPoolSize: 50,
  connectionAcquisitionTimeout: 60000,
})
```

---

## 🚨 장애 대응

### 롤백 계획

**Frontend (Vercel)**:
```bash
# 이전 버전으로 롤백
vercel rollback
```

**Custom App (PM2)**:
```bash
# 이전 버전으로 롤백
git checkout previous-commit
npm install
pm2 restart shopify-app
```

### Health Checks

```bash
# Frontend
curl https://nerdx.com/api/health

# Custom App
curl https://shopify-app.nerdx.com/health

# Neo4j
curl https://shopify-app.nerdx.com/ready
```

---

## 📞 지원 및 문서

### 주요 링크

- Frontend: https://nerdx.com
- Custom App: https://shopify-app.nerdx.com
- Shopify Store: https://nerdx.myshopify.com
- Admin Dashboard: https://nerdx.myshopify.com/admin

### 문서

- [Vercel 문서](https://vercel.com/docs)
- [Shopify 문서](https://shopify.dev/docs)
- [Neo4j Aura](https://neo4j.com/docs/aura/)

---

## 🎯 예상 비용 (월간)

| 서비스 | 플랜 | 비용 |
|--------|------|------|
| **Vercel** | Pro | $20 |
| **Shopify** | Shopify Plan | $79 |
| **AWS EC2** | t3.small | $15 |
| **Neo4j Aura** | Professional | $65 |
| **Redis Cloud** | Free | $0 |
| **도메인** | .com | $1 |
| **총계** | | **~$180/월** |

---

**배포 완료 예상 시간**: 4-6시간
**다음 단계**: Smoke Tests 및 성능 모니터링

---

*이 가이드를 따라 NERDX APEC MVP를 안전하게 Production 환경에 배포할 수 있습니다.*
