#!/bin/bash

# NERDX APEC Frontend Setup Script

set -e

echo "🚀 Starting NERDX APEC Frontend Setup..."

# Check Node version
echo "📦 Checking Node.js version..."
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Error: Node.js 18+ is required (found: $(node -v))"
    exit 1
fi
echo "✅ Node.js version: $(node -v)"

# Check npm version
echo "📦 Checking npm version..."
NPM_VERSION=$(npm -v | cut -d'.' -f1)
if [ "$NPM_VERSION" -lt 9 ]; then
    echo "❌ Error: npm 9+ is required (found: $(npm -v))"
    exit 1
fi
echo "✅ npm version: $(npm -v)"

# Install dependencies
echo "📥 Installing dependencies..."
npm install

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo "📝 Creating .env.local file..."
    cp .env.local.example .env.local
    echo "⚠️  Please update .env.local with your API keys"
else
    echo "✅ .env.local already exists"
fi

# Type check
echo "🔍 Running type check..."
npm run type-check

# Lint
echo "🧹 Running linter..."
npm run lint || true

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Update .env.local with your API keys"
echo "   2. Make sure the backend is running"
echo "   3. Run 'npm run dev' to start the development server"
echo ""
echo "🌐 The app will be available at http://localhost:3000"
echo ""
