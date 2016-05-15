import os
from unittest import TestCase
from urlparse import parse_qs
from lib.model.slack import SlackOAuthResponse, SlackResponseMessage, SlackException, SlackCommand, SlackResponseType

__author__ = 'bauerb'


class TestSlack(TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['SLACK_VERIFICATION_TOKEN'] = 'abcdef'

    # SlackOAuthResponse tests
    ##########################

    def create_valid_response(self):
        return {
            "body": {
                "access_token": "xoxp-XXXXXXXX-XXXXXXXX-XXXXX",
                "user_id": "usXX-XXXXXXXX-XXXXXXXX-XXXXX",
                "team_name": "Team Installing Your Hook",
                "team_id": "XXXXXXXXXX",
                "incoming_webhook": {
                    "url": "https://hooks.slack.com/TXXXXX/BXXXXX/XXXXXXXXXX",
                    "channel": "#channel-it-will-post-to",
                    "channel_id": "XXX-YYY",
                    "configuration_url": "https://teamname.slack.com/services/BXXXXX"
                }
            }
        }

    def create_invalid_response(self):
        return {
            "body": {
                "user_id": "usXX-XXXXXXXX-XXXXXXXX-XXXXX",
                "team_name": "Team Installing Your Hook",
                "team_id": "XXXXXXXXXX",
                "incoming_webhook": {
                    "channel": "#channel-it-will-post-to",
                    "channel_id": "XXX-YYY",
                    "configuration_url": "https://teamname.slack.com/services/BXXXXX"
                }
            }
        }

    def test_valid_slack_oauth_response(self):
        response = self.create_valid_response()
        SlackOAuthResponse(response['body'])

    def test_invalid_slack_oauth_response(self):
        response = self.create_invalid_response()
        with self.assertRaises(KeyError):
            SlackOAuthResponse(response['body'])

    # SlackResponseMessage tests
    ############################

    def test_slack_response_message(self):
        message = 'some text'
        response_message = SlackResponseMessage(message).build()
        self.assertEqual({'response_type': 'ephemeral', 'text': message}, response_message)

    def test_slack_response_message_invalid_channel(self):
        message = 'some text'
        response_message = SlackResponseMessage(message).build()
        self.assertEqual({'response_type': 'ephemeral', 'text': message}, response_message)

    def test_slack_response_message_in_channel(self):
        message = 'some text'
        respone_type = SlackResponseType.in_channel
        response_message = SlackResponseMessage(message, respone_type).build()
        self.assertEqual({'response_type': 'in_channel', 'text': message}, response_message)

    # SlackException tests
    ######################

    def test_slack_exception(self):
        error_message = 'some error'
        exception = SlackException(error_message)
        self.assertEqual(error_message, exception.message)
        self.assertIsInstance(exception, SlackException)
        self.assertIsInstance(exception, Exception)

        # SlackCommand tests

    ######################

    def test_slack_command_missing_token(self):
        body = parse_qs(
            "team_id=bla&team_domain=bla&channel_id=bla&"
            "channel_name=bla&user_id=bla&user_name=bla&command=%2Fbla&"
            "text=bla&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2Fbla")
        with self.assertRaises(SlackException) as e:
            SlackCommand(body)

        self.assertEquals("Error: Access denied. Message: Token is missing", e.exception.message)

    def test_slack_command_invalid_token(self):
        body = parse_qs(
            "token=bla&team_id=bla&team_domain=bla&channel_id=bla&"
            "channel_name=bla&user_id=bla&user_name=bla&command=%2Fbla&"
            "text=bla&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2Fbla")
        with self.assertRaises(SlackException) as e:
            SlackCommand(body)

        self.assertEquals("Error: Access denied. Message: Invalid token", e.exception.message)

    def test_slack_command_valid_token(self):
        body = parse_qs(
            "token=abcdef&team_id=bla&team_domain=bla&channel_id=bla&"
            "channel_name=bla&user_id=abc&user_name=John&command=%2Fbla&"
            "text=mycommand&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2Fbla")

        command = SlackCommand(body)
        self.assertEquals('abc', command.user_id)
        self.assertEquals('John', command.user_name)
        self.assertEquals('mycommand', command.text)

    def test_slack_command_missing_user_id(self):
        body = parse_qs(
            "token=abcdef&team_id=bla&team_domain=bla&channel_id=bla&"
            "channel_name=bla&user_name=John&command=%2Fbla&"
            "text=mycommand&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2Fbla")

        with self.assertRaises(KeyError) as e:
            SlackCommand(body)

        self.assertEquals('user_id', e.exception.message)
