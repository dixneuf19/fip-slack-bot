import json
from time import time, sleep
from typing import Tuple
from unittest.mock import patch

from slack_sdk.signature import SignatureVerifier
from slack_sdk.web import WebClient

from slack_bolt.app import App
from slack_bolt.request import BoltRequest
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.utils import remove_os_env_temporarily, restore_os_env

from fip_slack_bot.main import message_live
from fip_slack_bot.models import Track


class TestSlashCommand:
    signing_secret = "secret"
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
    signature_verifier = SignatureVerifier(signing_secret)
    web_client = WebClient(
        token=valid_token,
        base_url=mock_api_server_base_url,
    )

    def setup_method(self):
        self.old_os_env = remove_os_env_temporarily()
        setup_mock_web_api_server(self)

    def teardown_method(self):
        cleanup_mock_web_api_server(self)
        restore_os_env(self.old_os_env)

    def generate_signature(self, body: str, timestamp: str):
        return self.signature_verifier.generate_signature(
            body=body,
            timestamp=timestamp,
        )

    def build_headers(self, timestamp: str, body: str):
        return {
            "content-type": ["application/x-www-form-urlencoded"],
            "x-slack-signature": [self.generate_signature(body, timestamp)],
            "x-slack-request-timestamp": [timestamp],
        }

    def build_valid_request(self) -> BoltRequest:
        timestamp, body = str(int(time())), json.dumps(slash_command_body)
        return BoltRequest(body=body, headers=self.build_headers(timestamp, body))

    def test_mock_server_is_running(self):
        resp = self.web_client.api_test()
        assert resp != None

    def test_success(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        app.command("/hello-world")(commander)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert self.mock_received_requests["/auth.test"] == 1

    def test_process_before_response(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            process_before_response=True,
        )
        app.command("/hello-world")(commander)

        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 200
        assert self.mock_received_requests["/auth.test"] == 1

    def test_failure(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        request = self.build_valid_request()
        response = app.dispatch(request)
        assert response.status == 404
        assert self.mock_received_requests["/auth.test"] == 1

        app.command("/another-one")(commander)
        response = app.dispatch(request)
        assert response.status == 404
        assert self.mock_received_requests["/auth.test"] == 1

    # Custom part

    def build_custom_valid_request(self, slash_body: Tuple[str]) -> BoltRequest:
        timestamp, body = str(int(time())), json.dumps(slash_body)
        return BoltRequest(body=body, headers=self.build_headers(timestamp, body))

    def test_message_live(self, mocker):

        mocker.patch(
            "fip_slack_bot.main.get_live_on_FIP", return_value=resp_get_live_on_FIP
        )

        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )

        app.command("/whatsonfip")(message_live)

        request = self.build_custom_valid_request(whatsonfip_command_body)

        response = app.dispatch(request)
        # might be asynchronous
        sleep(0.1)
        assert response.status == 200
        assert self.mock_received_requests["/auth.test"] == 1
        print(self.mock_received_requests_body)


resp_get_live_on_FIP = Track(
    **{
        "title": "Root down (and get it)",
        "album": "Root down (live)",
        "artist": "Jimmy Smith",
        "year": 1972,
        "label": "VERVE",
        "musical_kind": "Jazz ",
        "external_urls": {
            "deezer": "https://www.deezer.com/track/2461366",
            "itunes": "https://music.apple.com/fr/album/root-down-and-get-it-alternate-take/1442939892?i=1442940484&uo=4",
            "spotify": "https://open.spotify.com/track/19PG9tIlRRi56n7Tgywkxm",
        },
        "cover_url": "https://cdn.radiofrance.fr/s3/cruiser-production/2019/12/afe28a90-5f53-46f9-b8ad-f0afa0c59c4d/266x266_rf_omm_0000230568_dnc.0057956636.jpg",
    }
)

whatsonfip_command_body = (
    "token=verification_token"
    "&team_id=T111"
    "&team_domain=loudnaround.org"
    "&channel_id=C111"
    "&channel_name=fip"
    "&user_id=W111"
    "&user_name=baloo"
    "&command=%2Fwhatsonfip"
    "&text="
    "&enterprise_id=E111"
    "&enterprise_name=LNA"
    "&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT111%2F111%2Fxxxxx"
    "&trigger_id=111.111.xxx"
)

# whatsonfip_command_result =

slash_command_body = (
    "token=verification_token"
    "&team_id=T111"
    "&team_domain=test-domain"
    "&channel_id=C111"
    "&channel_name=random"
    "&user_id=W111"
    "&user_name=primary-owner"
    "&command=%2Fhello-world"
    "&text=Hi"
    "&enterprise_id=E111"
    "&enterprise_name=Org+Name"
    "&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT111%2F111%2Fxxxxx"
    "&trigger_id=111.111.xxx"
)


def commander(ack, body, payload, command):
    assert body == command
    assert payload == command
    ack()
