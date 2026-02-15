# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies (Node.js/npm)
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /usr/src/app

# COPY requirements.txt first
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# COPY package.json for backend
COPY package*.json ./
RUN npm install

# COPY frontend package.json for build
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install

# Bundle app source
COPY . .

# Build Frontend
RUN cd frontend && npm run build

# Expose the API port
EXPOSE 3000

# Define environment variable
ENV PORT=3000

# Run the app
CMD ["node", "index.js"]
