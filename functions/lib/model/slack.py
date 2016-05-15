import logging
import os
from enum import Enum

__author__ = 'bauerb'

log = logging.getLogger()
log.setLevel(logging.DEBUG)


class SlackResponseType(Enum):
    ephemeral = 'ephemeral'
    in_channel = 'in_channel'


slack_response_types = [SlackResponseType.ephemeral, SlackResponseType.in_channel]


class SlackResponseMessage(object):
    def __init__(self, text, response_type=SlackResponseType.ephemeral):
        self.text = text

        if response_type in slack_response_types:
            self.response_type = response_type
        else:
            self.response_type = SlackResponseType.ephemeral
            log.warning(
                "Invalid response_type {}. response_type was set to {}".format(response_type, self.response_type))

    def build(self):
        return {'response_type': self.response_type, 'text': self.text}


class SlackException(Exception):
    def __init__(self, message):
        self.message = message


class SlackOAuthResponse(object):
    def __init__(self, body):
        self.access_token = body['access_token']
        self.user_id = body['user_id']
        incoming_webhook = body['incoming_webhook']
        self.incoming_webhook_url = incoming_webhook['url']
        self.channel_id = incoming_webhook['channel_id']
        self.channel_name = incoming_webhook['channel']
        self.configuration_url = incoming_webhook['configuration_url']
        self.team_id = body['team_id']
        self.team_name = body['team_name']


class SlackCommand(object):
    def __init__(self, body):
        if 'token' not in body.keys():
            error = "Error: {}. Message: {}".format('Access denied', 'Token is missing')
            log.debug(error)
            raise SlackException(error)

        if body['token'][0] != os.getenv('SLACK_VERIFICATION_TOKEN'):
            error = "Error: {}. Message: {}".format('Access denied', 'Invalid token')
            log.debug(error)
            raise SlackException(error)

        if not body['text']:
            error = "Error: {}. Message: {}".format('Bad Request', 'Command is missing')
            log.debug(error)
            raise SlackException(error)

        self.text = body['text'][0]
        self.user_id = body['user_id'][0]
        self.user_name = body['user_name'][0]
        self.channel_name = body['channel_name'][0]
        self.channel_id = body['channel_id'][0]
