FROM node:22-alpine AS builder

WORKDIR /app

ARG VITE_API_BASE=""
ARG VITE_COGNITO_REGION
ARG VITE_COGNITO_CLIENT_ID

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
