from prometheus_client import Gauge, Counter, Summary, Histogram


class Prom:
    SEND_VOICE_NOTIFICATION = Summary('send_voice_notification_latency_seconds', 'Time spent processing send voice notification')
