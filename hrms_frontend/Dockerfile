# Build stage
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Accept build arguments for Asgardeo configuration
ARG VITE_CLIENT_ID=""
ARG VITE_ORG_BASE_URL=""

# Create .env.production file with build arguments
RUN echo "VITE_CLIENT_ID=${VITE_CLIENT_ID}" > .env.production && \
    echo "VITE_ORG_BASE_URL=${VITE_ORG_BASE_URL}" >> .env.production

# Build the application
RUN npm run build

# Production stage
FROM node:22-alpine

WORKDIR /app

# Install serve to run the production build
RUN npm install -g serve

# Copy built application from builder
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Start the application
CMD ["serve", "-s", "dist", "-l", "3000"]
