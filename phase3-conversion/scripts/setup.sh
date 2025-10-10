#!/bin/bash

# Phase 3: Conversion Setup Script
# This script helps set up the Phase 3 development environment

set -e

echo "================================"
echo "Phase 3: Conversion Setup"
echo "================================"
echo ""

# Check Node.js version
echo "Checking Node.js version..."
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "Error: Node.js 18 or higher is required"
    echo "Current version: $(node -v)"
    exit 1
fi
echo "Node.js version: $(node -v) ✓"
echo ""

# Check npm version
echo "Checking npm version..."
NPM_VERSION=$(npm -v | cut -d'.' -f1)
if [ "$NPM_VERSION" -lt 9 ]; then
    echo "Warning: npm 9 or higher is recommended"
    echo "Current version: $(npm -v)"
fi
echo "npm version: $(npm -v) ✓"
echo ""

# Install dependencies
echo "Installing dependencies..."
npm install
echo "Dependencies installed ✓"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ".env file created ✓"
    echo ""
    echo "⚠️  IMPORTANT: Please update .env with your configuration:"
    echo "   - STRIPE_SECRET_KEY"
    echo "   - STRIPE_PUBLISHABLE_KEY"
    echo "   - STRIPE_WEBHOOK_SECRET"
    echo "   - PHASE1_API_URL"
    echo ""
else
    echo ".env file already exists ✓"
    echo ""
fi

# Create logs directory
echo "Creating logs directory..."
mkdir -p logs
echo "Logs directory created ✓"
echo ""

# Check Stripe CLI installation (optional)
echo "Checking for Stripe CLI..."
if command -v stripe &> /dev/null; then
    echo "Stripe CLI found: $(stripe --version) ✓"
    echo ""
    echo "To test webhooks locally, run:"
    echo "  stripe listen --forward-to localhost:3003/api/webhooks/stripe"
    echo ""
else
    echo "Stripe CLI not found (optional)"
    echo "Install from: https://stripe.com/docs/stripe-cli"
    echo ""
fi

# Check Docker installation (optional)
echo "Checking for Docker..."
if command -v docker &> /dev/null; then
    echo "Docker found: $(docker --version) ✓"
    echo ""
    echo "To run with Docker:"
    echo "  docker-compose up -d"
    echo ""
else
    echo "Docker not found (optional)"
    echo ""
fi

# Summary
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Update .env file with your Stripe credentials"
echo "   Get your keys from: https://dashboard.stripe.com/apikeys"
echo ""
echo "2. Ensure Phase 1 API is running at the configured URL"
echo "   Default: http://localhost:3001/api"
echo ""
echo "3. Start the development server:"
echo "   npm run dev"
echo ""
echo "4. (Optional) Set up Stripe webhook forwarding:"
echo "   stripe listen --forward-to localhost:3003/api/webhooks/stripe"
echo ""
echo "5. Test the API:"
echo "   curl http://localhost:3003/health"
echo ""
echo "6. Import postman_collection.json for API testing"
echo ""
echo "For more information, see README.md"
echo ""
