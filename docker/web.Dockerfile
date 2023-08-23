## First stage, build the web app
FROM node:20 as webapp-build

RUN mkdir /Lires
WORKDIR /

COPY . /Lires
WORKDIR /Lires/lires_web 
RUN npm install -g cnpm --registry=https://registry.npm.taobao.org
RUN cnpm install && cnpm run build

## Second stage, build the server
FROM nginx:bookworm as nginx-server
COPY --from=webapp-build /Lires/lires_web/dist /usr/share/nginx/html

# https://hub.docker.com/_/nginx/
EXPOSE 80