from twilio.rest import Client
import harp_notifications_voice.settings as settings
from logger.logging import service_logger
import requests
import traceback
from harp_notifications_voice.metrics.service_monitoring import Prom
from harp_notifications_voice.logic.get_bot_config import bot_config

logger = service_logger()


class VoiceNotifications(object):
    def __init__(self, twilio_account_sid, twilio_auth_token, twilio_phone_number):
        self.twilio_account_sid = twilio_account_sid
        self.twilio_auth_token = twilio_auth_token
        self.twilio_phone_number = twilio_phone_number
        self.bot_config = self.get_bot_config()
        self.client = Client(self.bot_config['TWILIO_ACCOUNT_SID'], self.bot_config['TWILIO_AUTH_TOKEN'])

    def get_bot_config(self):
        if self.twilio_account_sid:
            config = {
                'TWILIO_ACCOUNT_SID': self.twilio_account_sid,
                'TWILIO_AUTH_TOKEN': self.twilio_auth_token,
                'TWILIO_PHONE_NUMBER': self.twilio_phone_number
            }
        else:
            config = bot_config(bot_name='voice')

        return config

    def check_status(self, sid):
        call = self.client.calls.get(sid=sid).fetch()

        status = {
            'sid': call.sid,
            'status': call.status,
            'price': call.price,
            'price_unit': call.price_unit,
            'duration': call.duration,
            'queue_time': call.queue_time
        }

        return status

    @Prom.SEND_VOICE_NOTIFICATION.time()
    def create_notification(self, to_number: str, body: str):
        xml_string = f"""<Response><Say voice="man">{body}</Say><Hangup/></Response>"""

        logger.info(msg=f"String to call: {xml_string}")

        call = self.client.calls.create(
            twiml=xml_string,
            to=to_number,
            from_=self.bot_config['TWILIO_PHONE_NUMBER']
        )

        status = {
            'sid': call.sid,
            'status': call.status,
            'price': call.price,
            'price_unit': call.price_unit,
            'duration': call.duration,
            'queue_time': call.queue_time
        }

        logger.info(msg=f"Person received the call: {status}")

        return status
