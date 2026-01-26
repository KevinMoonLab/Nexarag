# Build stage
FROM node:18-alpine AS build
WORKDIR /app

# Set npm to skip optional dependencies and use legacy peer deps
RUN npm config set fund false
RUN npm config set audit false
RUN npm config set legacy-peer-deps true

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies with specific flags for compatibility
RUN npm ci --only=production=false --platform=linux --arch=x64 || npm install --platform=linux --arch=x64

# Copy application source
COPY . .

RUN npm install -g nx

# Build application
RUN nx build litreview -c production --verbose

# Production stage with NGINX
FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Remove default NGINX static assets
RUN rm -rf ./*

# Copy built assets from the build stage
COPY --from=build /app/dist/litreview/browser ./litreview

# Copy custom NGINX configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy custom mime.types
COPY mime.types /etc/nginx/mime.types

# Expose port 80 
EXPOSE 80

# Start NGINX
CMD ["nginx", "-g", "daemon off;"]