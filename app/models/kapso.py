from pydantic import BaseModel, root_validator
from enum import StrEnum
from typing import Literal

class KapsoMessageType(StrEnum):
    TEXT = "text"
    INTERACTIVE = "interactive"
    IMAGE = "image"

class KapsoInteractiveType(StrEnum):
    LIST = "list"
    BUTTON = "button"

class BaseKapsoBody(BaseModel):
    messaging_product: str = Literal["whatsapp"]
    to: str
    type: KapsoMessageType

class KapsoBody(BaseModel):
    body: str


class KapsoReply(BaseModel):
    id: str
    title: str

class KapsoButton(BaseModel):
    type: str = Literal["reply"]
    reply: KapsoReply

class KapsoRow(BaseModel):
    id: str
    title: str
    description: str

class KapsoSection(BaseModel):
    title: str
    rows: list[KapsoRow]


class KapsoAction(BaseModel):
    buttons: list[KapsoButton] | None = None
    sections: list[KapsoSection] | None = None
    button: KapsoButton | None = None

    @root_validator(pre=True)
    def validate_action(cls, values):
        buttons = values.get("buttons")
        sections = values.get("sections")
        button = values.get("button")

        # Validation: either (sections and button) or (buttons)
        if (sections is not None and button is not None) and (buttons is None):
            return values
        elif (buttons is not None) and (sections is None and button is None):
            return values
        else:
            raise ValueError("KapsoAction must have either both 'sections' and 'button', or 'buttons' (not both or partial).")

class KapsoInteractiveBody(BaseModel):
    type: KapsoInteractiveType
    body: KapsoBody
    action: KapsoAction

class KapsoInteractiveMessage(BaseKapsoBody):
    interactive: KapsoInteractiveBody

class KapsoTextMessage(BaseKapsoBody):
    text: KapsoBody