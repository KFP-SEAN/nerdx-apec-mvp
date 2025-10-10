# Quick Start Guide

Get the NERDX APEC frontend up and running in minutes!

## Prerequisites

- Node.js 18+ installed
- npm 9+ installed
- Backend API running (see backend README)

## Option 1: Quick Setup (Recommended)

```bash
# Run the setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Option 2: Manual Setup

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Edit .env.local with your API keys
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx

# Start development server
npm run dev
```

## Option 3: Docker

```bash
# Build and run with Docker
chmod +x scripts/build-docker.sh
./scripts/build-docker.sh

# Or use docker-compose
docker-compose up -d
```

## Environment Variables

Create `.env.local` with:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
```

## Test the Setup

1. **Landing Page**: Visit [http://localhost:3000](http://localhost:3000)
2. **Products**: Go to [http://localhost:3000/products](http://localhost:3000/products)
3. **Chat**: Try [http://localhost:3000/chat](http://localhost:3000/chat)
4. **CAMEO**: Create at [http://localhost:3000/cameo](http://localhost:3000/cameo)

## Common Issues

### Port 3000 in use
```bash
# Kill process on port 3000
npx kill-port 3000
# Or use different port
PORT=3001 npm run dev
```

### Module not found
```bash
# Clear and reinstall
rm -rf node_modules .next
npm install
```

### API connection fails
- Check backend is running on port 8000
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Check CORS settings on backend

## Next Steps

- Read the [full README](README.md) for detailed documentation
- Check [component documentation](README.md#component-usage)
- Learn about [API integration](README.md#api-integration)

## Need Help?

- Email: support@nerdx-apec.com
- Documentation: See README.md
- Backend API: Check backend/README.md

---

Happy coding! 🚀
