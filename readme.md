# Pizza One Hit Discord Bot
### for docker:
```
docker run -d --mount src="/opt/pizzaonehitai/sharedpath",target=/pizzaonehitai/sharedpath,type=bind \
-e DC_TOKEN=$(cat /opt/pizzaonehitai/sharedpath/token.tkn) \
-e RIOT_API_TOKEN=$(cat /opt/pizzaonehitai/sharedpath/riot-api-key) \
--name p1h-discord-bot \
mkrzeszewski/pizzaonehit-discord-bot:latest
```
### clearing old containers:
```
for container in $(docker ps -a | awk '{print $1}'); do docker rm $container; done;
```
### for docker compose
```
version: '3'

services:
   p1h-discord-bot:
    container_name: discord-bot
    image: mkrzeszewski/pizzaonehit-discord-bot:multiarch-env-tokens
    restart: unless-stopped
    volumes:
      - /opt/pizzaonehitai/pizzaonehitai/plugins:/pizzaonehitai/plugins
    environment:
        RIOT_API_TOKEN: <>
        DC_TOKEN: <>
        MONGO_USERNAME: <>
        MONGO_PASSWORD: <>
        MONGO_ENDPOINT: mongo:27017
        DISCORD_CHANNEL_TFT: <>
        PROD_STATUS: PRODUCTION / DEVELOPEMENT
        DEBUG_MODE: True
        GOOGLE_MAPS_API_KEY: <>
```
