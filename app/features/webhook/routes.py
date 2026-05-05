import os

from dotenv import load_dotenv
from flask import abort, request

from app.features.webhook import webhook_bp
from app.features.webhook.services import WebhookService

load_dotenv()

WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN")

webhook_service = WebhookService()


@webhook_bp.route("/webhook/deploy", methods=["POST"])
def deploy():
    if request.headers.get("Authorization") != f"Bearer {WEBHOOK_TOKEN}":
        abort(403, description="Unauthorized")

    webhook_service.deploy()
    return "Deployment successful", 200
