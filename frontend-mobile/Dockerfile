FROM node:18-alpine

WORKDIR /app

# Install Expo CLI
RUN npm install -g expo-cli

COPY package.json package-lock.json ./

RUN npm ci

COPY . .

EXPOSE 8081 19000 19001

CMD ["npm", "start"]
