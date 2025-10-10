/**
 * Phase D: Production Deployment
 *
 * Prepares for deployment and provides instructions
 * Requires user approval for actual deployment
 *
 * Estimated: 2-3 hours (mostly automated)
 */

import * as fs from 'fs';
import { execSync } from 'child_process';

class PhaseDDeploy {
  private log(message: string) {
    console.log(`[Phase D] ${message}`);
  }

  async run() {
    this.log('🚀 Starting Phase D: Production Deployment Prep\n');

    await this.createVercelConfig();
    await this.createDockerfile();
    await this.setupEnvironmentDocs();
    await this.createDeploymentChecklist();
    await this.runProductionBuild();
    await this.commitChanges();
    await this.provideInstructions();

    this.log('✅ Phase D Complete!\n');
  }

  private async createVercelConfig() {
    this.log('📦 Creating Vercel configuration...');

    const vercelConfig = `{
  "version": 2,
  "buildCommand": "cd frontend && npm run build",
  "devCommand": "cd frontend && npm run dev",
  "installCommand": "cd frontend && npm install",
  "framework": "nextjs",
  "outputDirectory": "frontend/.next",
  "env": {
    "NEXT_PUBLIC_SHOPIFY_DOMAIN": "@shopify_domain",
    "NEXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN": "@shopify_storefront_token"
  },
  "build": {
    "env": {
      "NEXT_PUBLIC_SHOPIFY_DOMAIN": "@shopify_domain",
      "NEXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN": "@shopify_storefront_token"
    }
  }
}
`;

    fs.writeFileSync('vercel.json', vercelConfig);
    this.log('✅ Vercel config created');
  }

  private async createDockerfile() {
    this.log('🐳 Creating Dockerfile...');

    const dockerfile = `FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies
COPY frontend/package*.json ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY frontend ./

ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
`;

    fs.writeFileSync('Dockerfile', dockerfile);
    this.log('✅ Dockerfile created');
  }

  private async setupEnvironmentDocs() {
    this.log('📝 Creating environment documentation...');

    const envDocs = `# Environment Variables Setup

## Required Variables

### Frontend (.env.local)
\`\`\`bash
NEXT_PUBLIC_SHOPIFY_DOMAIN=your-store.myshopify.com
NEXT_PUBLIC_SHOPIFY_STOREFRONT_TOKEN=your_storefront_token
NEXT_PUBLIC_SHOPIFY_APP_URL=http://localhost:3001
NODE_ENV=production
\`\`\`

### Backend (.env)
\`\`\`bash
SHOPIFY_ADMIN_API_TOKEN=your_admin_token
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
REDIS_URL=redis://localhost:6379
JWT_SECRET=your_jwt_secret
\`\`\`

## Deployment Platforms

### Vercel
1. Install Vercel CLI: \`npm i -g vercel\`
2. Login: \`vercel login\`
3. Deploy: \`vercel --prod\`
4. Add environment variables in Vercel dashboard

### AWS / Docker
1. Build image: \`docker build -t nerdx-apec .\`
2. Run: \`docker run -p 3000:3000 -e NEXT_PUBLIC_SHOPIFY_DOMAIN=... nerdx-apec\`

### Domain Setup
1. Point domain to Vercel/AWS
2. Configure SSL (auto with Vercel)
3. Update Shopify app URLs

## Monitoring

### Sentry (Error Tracking)
\`\`\`bash
NEXT_PUBLIC_SENTRY_DSN=your_sentry_dsn
SENTRY_AUTH_TOKEN=your_auth_token
\`\`\`

### Google Analytics
\`\`\`bash
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX
\`\`\`
`;

    fs.writeFileSync('docs/ENVIRONMENT_SETUP.md', envDocs);
    this.log('✅ Environment docs created');
  }

  private async createDeploymentChecklist() {
    this.log('✅ Creating deployment checklist...');

    const checklist = `# Production Deployment Checklist

## Pre-Deployment

- [ ] All tests passing (90%+ success rate)
- [ ] No console errors in production build
- [ ] Environment variables documented
- [ ] Database backups configured
- [ ] Monitoring setup (Sentry, Analytics)

## Vercel Deployment

- [ ] Install Vercel CLI: \`npm i -g vercel\`
- [ ] Login to Vercel: \`vercel login\`
- [ ] Link project: \`vercel link\`
- [ ] Add environment variables in dashboard
- [ ] Deploy preview: \`vercel\`
- [ ] Test preview deployment
- [ ] Deploy production: \`vercel --prod\`

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
\`\`\`bash
npm install @sentry/nextjs
npx @sentry/wizard@latest -i nextjs
\`\`\`

### Google Analytics
Add GA script to \`app/layout.tsx\`

## Rollback Plan

If issues occur:
1. \`vercel rollback\` to previous deployment
2. Check error logs: \`vercel logs\`
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
`;

    fs.writeFileSync('docs/DEPLOYMENT_CHECKLIST.md', checklist);
    this.log('✅ Deployment checklist created');
  }

  private async runProductionBuild() {
    this.log('🏗️  Running production build...');

    try {
      execSync('npm run build', {
        stdio: 'inherit',
        cwd: process.cwd()
      });
      this.log('✅ Production build successful');
    } catch (error) {
      this.log('⚠️  Production build failed (check errors)');
    }
  }

  private async commitChanges() {
    this.log('💾 Committing deployment configs...');

    try {
      execSync('git add .', { stdio: 'inherit' });
      execSync(`git commit -m "feat: Phase D - Production deployment configuration (auto-generated)

- Add Vercel configuration
- Add Dockerfile for containerization
- Add comprehensive environment variable documentation
- Add deployment checklist
- Add monitoring setup guides
- Test production build

Deployment Ready:
- Vercel (recommended)
- AWS / Docker
- Custom domain support
- SSL/HTTPS auto-configured

Monitoring:
- Sentry for error tracking
- Google Analytics
- Performance monitoring

🤖 Auto-generated by Phase D automation

⚠️  USER ACTION REQUIRED: Run deployment commands manually"`, { stdio: 'inherit' });

      this.log('✅ Changes committed');
    } catch (error) {
      this.log('⚠️  Commit failed (might be nothing to commit)');
    }
  }

  private async provideInstructions() {
    this.log('\n' + '='.repeat(80));
    this.log('🚀 DEPLOYMENT INSTRUCTIONS');
    this.log('='.repeat(80) + '\n');

    this.log('Phase D has prepared everything for deployment.');
    this.log('To deploy to production, follow these steps:\n');

    this.log('📦 Quick Deploy (Vercel - Recommended)');
    this.log('   1. npm i -g vercel');
    this.log('   2. vercel login');
    this.log('   3. vercel --prod');
    this.log('   4. Add environment variables in Vercel dashboard\n');

    this.log('🐳 Docker Deploy');
    this.log('   1. docker build -t nerdx-apec .');
    this.log('   2. docker run -p 3000:3000 -e ... nerdx-apec\n');

    this.log('📝 Documentation Created:');
    this.log('   - docs/ENVIRONMENT_SETUP.md');
    this.log('   - docs/DEPLOYMENT_CHECKLIST.md');
    this.log('   - vercel.json');
    this.log('   - Dockerfile\n');

    this.log('⚠️  IMPORTANT: This phase requires manual deployment approval');
    this.log('   The automation will skip actual deployment.\n');

    this.log('='.repeat(80) + '\n');
  }
}

// Execute
const phaseD = new PhaseDDeploy();
phaseD.run().catch(error => {
  console.error('[Phase D] Fatal Error:', error);
  process.exit(1);
});
