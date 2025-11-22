from app.models.kapso import (
    KapsoBody,
    KapsoTextMessage,
    KapsoMessageType,
    KapsoInteractiveBody,
    KapsoInteractiveType,
    KapsoAction,
    KapsoButton,
    KapsoInteractiveMessage,
    KapsoRow,
    KapsoSection,
)
from app.config import settings
import requests


def send_kapso_request(endpoint: str, body: KapsoBody, method: str = "POST") -> None:
    if not settings.KAPSO_URL or not settings.KAPSO_PHONE_NUMBER_ID:
        raise ValueError("KAPSO_URL and KAPSO_PHONE_NUMBER_ID must be configured")
    
    url = f"{settings.KAPSO_URL}/{settings.KAPSO_PHONE_NUMBER_ID}/{endpoint}"
    headers = {
        "X-API-Key": settings.KAPSO_API_KEY,
        "Content-Type": "application/json",
    }
    response = requests.request(method, url, headers=headers, data=body.model_dump())
    response.raise_for_status()


def send_text_message(receiver: str, message: str) -> None:
    body = KapsoTextMessage(
        to=receiver,
        type=KapsoMessageType.TEXT,
        text=KapsoBody(body=message),
    )
    send_kapso_request("messages", body)


def send_buttons_message(receiver: str, title: str, buttons: list[KapsoButton]) -> None:
    body = KapsoInteractiveMessage(
        to=receiver,
        type=KapsoMessageType.INTERACTIVE,
        interactive=KapsoInteractiveBody(
            type=KapsoInteractiveType.BUTTON,
            body=KapsoBody(body=title),
            action=KapsoAction(buttons=buttons),
        ),
    )
    send_kapso_request("messages", body)


def send_list_message(receiver: str, title: str, rows: list[KapsoRow]) -> None:
    body = KapsoInteractiveMessage(
        to=receiver,
        type=KapsoMessageType.INTERACTIVE,
        interactive=KapsoInteractiveBody(
            type=KapsoInteractiveType.LIST,
            body=KapsoBody(body=title),
            action=KapsoAction(sections=[KapsoSection(title=title, rows=rows)]),
        ),
    )
    send_kapso_request("messages", body)
