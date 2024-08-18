FROM node:16-alpine

# Install serve
RUN npm install -g serve

# Set the working directory
WORKDIR /src

# Install dependencies
COPY ./src/package*.json .
RUN npm install
COPY ./src/ .

# Build the React app
RUN npm run build