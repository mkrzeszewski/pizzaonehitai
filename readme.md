# Pizza One Hit Discord Bot
### for docker:
```
docker run --mount src="/opt/pizzaonehitai/sharedpath",target=/pizzaonehit/sharedpath,type=bind -e DC_TOKEN=$(cat /opt/pizzaonehitai/sharedpath/token.tkn) -e RIOT_API_TOKEN=$(cat /opt/pizzaonehitai/sharedpath/riot-api-key) mkrzeszewski/pizzaonehit-discord-bot:multiarch-env-tokens
```
