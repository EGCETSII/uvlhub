from splent_framework.repositories.BaseRepository import BaseRepository

from app.features.webhook.models import Webhook


class WebhookRepository(BaseRepository):
    def __init__(self):
        super().__init__(Webhook)
