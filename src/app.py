import os

BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
try:
    CHANNEL_TOKEN = os.environ["DEFAULT_SLACK_CHANNEL"]
except KeyError as e:
    CHANNEL_TOKEN = None
    
    
print(BOT_TOKEN)
print(APP_TOKEN)
print(CHANNEL_TOKEN)