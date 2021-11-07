import os

from dotenv import load_dotenv
from loguru import logger

from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore


from fip_slack_bot.fmt import get_blocks, get_text
from fip_slack_bot.api import get_live_on_FIP, LiveFIPException, get_live_on_meuh
from fip_slack_bot.models import FIP_RADIO, MEUH_RADIO

load_dotenv()

oauth_settings = OAuthSettings(
    client_id=os.environ.get("SLACK_CLIENT_ID"),
    client_secret=os.environ.get("SLACK_CLIENT_SECRET"),
    scopes=["commands", "chat:write"],
    installation_store=FileInstallationStore(base_dir="./data"),
    state_store=FileOAuthStateStore(expiration_seconds=600, base_dir="./data"),
    install_page_rendering_enabled=False,
)

# Initializes your app with your bot token and signing secret
app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"), oauth_settings=oauth_settings
)
app_handler = SlackRequestHandler(app)


@app.command("/whatsonfip")
def message_live(ack, say, command):
    logger.info(
        f"Received /whatsonfip command from {command['user_name']} in {command['channel_name']} - {command['team_domain']}"
    )
    ack()
    try:
        track = get_live_on_FIP()
    except LiveFIPException:
        say(text="No live song information right now, is it _Club Jazzafip_ ?")
    else:
        logger.debug(f"Fetched from FIP API: {track}")
        blocks = get_blocks(track, FIP_RADIO, command["user_id"])
        text = get_text(track)
        say(blocks=blocks, text=text)


@app.command("/meuh")
def message_meuh(ack, say, command):
    logger.info(
        f"Received /meuh command from {command['user_name']} in {command['channel_name']} - {command['team_domain']}"
    )
    ack()
    track = get_live_on_meuh()
    logger.debug(f"Fetched from FIP API: {track}")
    blocks = get_blocks(track, MEUH_RADIO, command["user_id"])
    text = get_text(track)
    print(blocks)
    say(blocks=blocks, text=text)


from fastapi import FastAPI, Request

api = FastAPI()


@api.post("/slack/events")
async def endpoint(req: Request):
    return await app_handler.handle(req)


@api.get("/slack/install")
async def install(req: Request):
    return await app_handler.handle(req)


@api.get("/slack/oauth_redirect")
async def oauth_redirect(req: Request):
    return await app_handler.handle(req)


@api.get("/health")
async def get_health():
    return {"message": "OK"}
