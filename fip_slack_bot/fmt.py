from typing import Dict, Any, List

from fip_slack_bot.models import Track, ExternalURL

external_url_provider_order = ["spotify", "youtube", "deezer", "itunes"]

fip_radio_section = {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Live on FIP !*"
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Listen :radio:",
					"emoji": True
				},
				"value": "Listen to FIP",
				"url": "https://www.fip.fr",
				"action_id": "FIP"
			}
		}

default_context = 	{
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://upload.wikimedia.org/wikipedia/fr/thumb/d/d5/FIP_logo_2005.svg/240px-FIP_logo_2005.svg.png",
					"alt_text": "FIP"
				},
				{
					"type": "mrkdwn",
					"text": "Try */whatsonfip* yourself !\n"
				}
			]
		}

telegram_context = {
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/200px-Telegram_logo.svg.png",
					"alt_text": "Telegram"
				},
				{
					"type": "mrkdwn",
					"text": "Also available on _Telegram_ @FIP_radio_bot"
				}
			]
		}

def get_external_url_provider_name(external_url_provider: str) -> str:
    if external_url_provider == "itunes":
        return "iTunes"
    else:
        return external_url_provider.title()

def get_external_urls_sorted(track: Track) -> List[ExternalURL]:
    external_urls = []
    for provider in external_url_provider_order:
        if provider in track.external_urls:
            external_urls.append(
                ExternalURL(
                    provider=provider,
                    name=get_external_url_provider_name(provider),
                    url=track.external_urls[provider]
            ))
    return external_urls


def get_text(track: Track) -> str:
    text = f"*{track.title}*\n"
    text += f"_{track.artist}_\n"
    text += track.album
    if track.year:
        text += " - " + str(track.year) 
    
    return text

def get_track_section(track: Track) -> Dict[str, Any]:
    track_section =  {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": get_text(track)
			}}

    if track.cover_url:
        track_section["accessory"] = {
				"type": "image",
				"image_url": track.cover_url,
				"alt_text": f"{track.title}, by {track.artist}"
			}
    
    return track_section

def get_external_url_buttons(track: Track) -> List[Dict[str, Any]]:
    buttons = []
    for external_url in get_external_urls_sorted(track):
        buttons.append({
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": external_url.name,
						"emoji": True
					},
					"value": f"Listen on {external_url.name}",
					"url": external_url.url,
					"action_id": external_url.provider
				})
    return buttons

def get_blocks(track: Track) -> List[Dict[str, Any]]:
    blocks = []

    blocks.append(fip_radio_section)

    blocks.append({"type": "divider"})

    blocks.append(get_track_section(track))

    if track.external_urls is not None and len(track.external_urls.keys()) > 0:
        blocks.append({"type": "divider"})
        blocks.append({
			"type": "actions",
			"elements": get_external_url_buttons(track)
		})
    
    blocks.append(default_context)

    return blocks
