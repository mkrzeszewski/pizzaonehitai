# Pizza One Hit Discord Bot
### for docker:
```
docker run -d --mount src="/opt/pizzaonehitai/sharedpath",target=/pizzaonehitai/sharedpath,type=bind \
-e DC_TOKEN=$(cat /opt/pizzaonehitai/sharedpath/token.tkn) \
-e RIOT_API_TOKEN=$(cat /opt/pizzaonehitai/sharedpath/riot-api-key) \
--name p1h-discord-bot \
mkrzeszewski/pizzaonehit-discord-bot:multiarch-env-tokens
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
    container_name: p1h-dc-bot
    image: mkrzeszewski/pizzaonehit-discord-bot:multiarch-env-tokens
    restart: unless-stopped
    volumes:
      - /opt/pizzaonehitai/sharedpath:/pizzaonehitai/sharedpath
    environment:
        RIOT_API_TOKEN: <YOUR RIOT TOKEN>
        DC_TOKEN: <YOUR DC TOKEN>
```