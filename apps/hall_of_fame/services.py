from .models import HallOfFame
import requests
import logging

logger = logging.getLogger(__name__)


def get_all_architects():
    return HallOfFame.objects.all()


def send_message_to_architect(architect_id, message):
    try:
        architect = HallOfFame.objects.get(id=architect_id)
        payload = {
            "topic": "Message from current Architect",
            "text": message,
            "target_emails": [architect.email],
        }

        try:
            response = requests.post(
                "http://docker_go:8080/send_letter",
                json=payload,
                timeout=3,
            )
            if response.status_code != 200:
                logger.error(f"Mailer error: {response.text}")
            else:
                logger.info(f"Message successfully sent to {architect.email}")
        except Exception as e:
            logger.exception(f"Failed to send mail via Go service: {e}")

        return True

    except HallOfFame.DoesNotExist:
        logger.warning(f"Architect with id={architect_id} not found.")
        return False
