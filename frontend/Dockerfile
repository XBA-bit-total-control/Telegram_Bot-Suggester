FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Next.js rewrites are resolved during build, so pass the Docker-internal API URL here.
ARG BACKEND_INTERNAL_URL=http://backend:8000
ENV BACKEND_INTERNAL_URL=${BACKEND_INTERNAL_URL}
ENV BACKEND_URL=${BACKEND_INTERNAL_URL}
ENV NODE_ENV=production

RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "start"]
