FROM node:22-alpine AS builder

WORKDIR /app

ARG VITE_API_BASE=""
ARG VITE_COGNITO_REGION="eu-central-1"
ARG VITE_COGNITO_CLIENT_ID

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:stable-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY --from=builder /app/scripts/entrypoint.sh /entrypoint.sh
COPY nginx.conf /etc/nginx/conf.d/default.conf
USER root
RUN chmod +x /entrypoint.sh \
    && chown -R nginx:nginx /usr/share/nginx/html /etc/nginx/conf.d /entrypoint.sh
USER nginx

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
