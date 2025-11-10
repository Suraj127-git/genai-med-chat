# Use official Node.js image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy only the vite-react folder content into /app
COPY vite-react/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the app
COPY vite-react ./

# Build the app
RUN npm run build

# Expose port for the dev server
EXPOSE 5173

# Start dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

