FROM node:16-alpine

# Install serve
RUN npm install -g serve

# Set the working directory
WORKDIR /src
COPY ./src/ .

# Install dependencies
#COPY ./src/package*.json .
#RUN npm install

# Build the React app
#RUN npm run build