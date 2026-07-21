import hmac
import os

from dotenv import load_dotenv
from flask import abort, jsonify, request

from app.features.webhook import webhook_bp
from app.features.webhook.services import WebhookService

load_dotenv()

webhook_service = WebhookService()


@webhook_bp.route("/webhook/deploy", methods=["POST"])
def deploy():
    # Read the token per request so configuration changes are picked up and an
    # unset variable can never be matched by a crafted "Bearer None" header.
    token = os.environ.get("WEBHOOK_TOKEN")
    if not token:
        return jsonify({"error": "Webhook token is not configured"}), 503

    authorization = request.headers.get("Authorization", "")
    if not hmac.compare_digest(authorization.encode("utf-8"), f"Bearer {token}".encode("utf-8")):
        abort(403, description="Unauthorized")

    webhook_service.deploy()
    return "Deployment successful", 200
