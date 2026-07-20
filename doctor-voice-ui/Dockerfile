FROM node:22-alpine AS build
WORKDIR /app
COPY . .

ARG VITE_API_BASE_URL
ARG VITE_RTC_BASE_URL
ARG VITE_WEBRTC_OFFER_PATH

ENV VITE_API_BASE_URL ${VITE_API_BASE_URL}
ENV VITE_RTC_BASE_URL ${VITE_RTC_BASE_URL}
ENV VITE_WEBRTC_OFFER_PATH ${VITE_WEBRTC_OFFER_PATH}

RUN npm install && npm run build

FROM nginx:stable-alpine AS production
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]