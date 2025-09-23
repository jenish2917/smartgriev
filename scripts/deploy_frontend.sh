#!/bin/bash
# SmartGriev Frontend Deployment Script

set -e

echo "Starting SmartGriev Frontend Deployment..."

# Install dependencies
echo "Installing dependencies..."
npm ci --only=production

# Run type checking
echo "Running TypeScript checks..."
npm run type-check

# Build for production
echo "Building production bundle..."
npm run build

# Check bundle size
echo "Checking bundle size..."
ls -lh dist/

echo "Frontend deployment completed successfully!"
echo "Built files are ready in: ./dist"