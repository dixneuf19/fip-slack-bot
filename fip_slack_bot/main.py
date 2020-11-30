import os

from dotenv import load_dotenv
from loguru import logger
from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore


from fip_slack_bot.fmt import get_blocks, get_text
from fip_slack_bot.api import get_live_on_FIP, LiveFIPException

load_dotenv()

oauth_settings = OAuthSettings(
    client_id=os.environ.get("SLACK_CLIENT_ID"),
    client_secret=os.environ.get("SLACK_CLIENT_SECRET"),
    scopes=["commands", "chat:write"],
    installation_store=FileInstallationStore(base_dir="./data"),
    state_store=FileOAuthStateStore(expiration_seconds=600, base_dir="./data")
)

# Initializes your app with your bot token and signing secret
app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    oauth_settings=oauth_settings
)

# Listens to incoming messages that contain "hello"
@app.command("/whatsonfip")
def message_live(ack, say, command):
    logger.info("Received /whatsonfip command")
    ack()
    try:
        track = get_live_on_FIP()
    except LiveFIPException:
        say(text="No live song information right now, is it _Club Jazzafip_ ?")
    else:
        logger.debug(f"Fetched from FIP API: {track}")
        blocks = get_blocks(track)
        text = get_text(track)
        say(blocks=blocks, text=text)


# Start your app
if __name__ == "__main__":
    logger.info("Starting server")
    app.start(port=int(os.environ.get("SERVER_PORT", 3000)))
    logger.info("Server started")
