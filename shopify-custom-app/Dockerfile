# ===================================
# Multi-stage Dockerfile for NERDX APEC Shopify Custom App
# Optimized for production deployment
# ===================================

# Stage 1: Base
FROM node:18-alpine AS base
LABEL maintainer="NERDX <dev@nerdx.com>"
LABEL description="NERDX APEC Shopify Custom App - AR Access Management"

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create app directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Stage 2: Dependencies
FROM base AS dependencies

# Install production dependencies
RUN npm ci --only=production --ignore-scripts && \
    npm cache clean --force

# Install dev dependencies for building
RUN npm ci --ignore-scripts

# Stage 3: Build (if needed for future TypeScript support)
FROM dependencies AS build
WORKDIR /app
COPY . .
# Add build steps here if needed (e.g., TypeScript compilation)
# RUN npm run build

# Stage 4: Production
FROM base AS production

# Set environment to production
ENV NODE_ENV=production \
    PORT=3000 \
    LOG_LEVEL=info

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy production dependencies from dependencies stage
COPY --from=dependencies --chown=nodejs:nodejs /app/node_modules ./node_modules

# Copy application code
COPY --chown=nodejs:nodejs . .

# Create logs directory
RUN mkdir -p logs && \
    chown -R nodejs:nodejs logs

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start application
CMD ["node", "server.js"]

# ===================================
# Build Instructions:
# docker build -t nerdx-apec-shopify:latest .
#
# Run Instructions:
# docker run -d \
#   --name nerdx-apec-shopify \
#   -p 3000:3000 \
#   --env-file .env \
#   nerdx-apec-shopify:latest
#
# Development with volume mount:
# docker run -d \
#   --name nerdx-apec-shopify-dev \
#   -p 3000:3000 \
#   --env-file .env \
#   -v $(pwd):/app \
#   -v /app/node_modules \
#   nerdx-apec-shopify:latest
# ===================================
