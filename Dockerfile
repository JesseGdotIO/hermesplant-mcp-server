FROM node:22-slim

WORKDIR /app

ENV NODE_ENV=production

COPY --chown=node:node mcp-server/package*.json ./
RUN npm ci --omit=dev --ignore-scripts --no-audit --no-fund

COPY --chown=node:node mcp-server/src ./src

ENV HERMES_BASE_URL=https://hermesplant.com
ENV HERMES_MCP_URL=https://hermesplant.com/mcp

USER node

CMD ["node", "src/server.js"]
