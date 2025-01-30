# Build stage
FROM node:18-alpine AS build
WORKDIR /app

# Copy application source
COPY . .

# Install dependencies
RUN npm install

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