FROM node:22-alpine AS builder

WORKDIR /app

ARG VITE_API_BASE=""
ARG VITE_COGNITO_CLIENT_ID
ARG VITE_REGISTRATION_ENABLED="false"
ARG VITE_AUTH_MODE="cognito"

# Re-export build args as env vars so Vite picks them up at `npm run build` time
ENV VITE_API_BASE=$VITE_API_BASE \
    VITE_COGNITO_CLIENT_ID=$VITE_COGNITO_CLIENT_ID \
    VITE_REGISTRATION_ENABLED=$VITE_REGISTRATION_ENABLED \
    VITE_AUTH_MODE=$VITE_AUTH_MODE

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
