"""Schemas and types for agent service."""

from enum import Enum
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Action types that the agent can perform."""

    CREATE_SESSION = "create_session"
    CLOSE_SESSION = "close_session"
    ASSIGN_ITEM_TO_USER = "assign_item_to_user"
    UNKNOWN = "unknown"
    # Más acciones se pueden agregar aquí en el futuro
    # CREATE_INVOICE = "create_invoice"
    # ADD_USER_TO_SESSION = "add_user_to_session"
    # CREATE_PAYMENT = "create_payment"


class CreateSessionData(BaseModel):
    """Schema for create session action data."""

    description: str


class CloseSessionData(BaseModel):
    """Schema for close session action data."""

    session_id: int | None = None
    session_description: str | None = None


class AssignItemToUserData(BaseModel):
    """Schema for assign item to user action data."""

    item_id: int | None = None
    user_id: int | None = None
    user_name: str | None = None
    invoice_id: int | None = None
    item_description: str | None = None


class UnknownActionData(BaseModel):
    """Schema for unknown action data."""

    reason: str | None = Field(
        None, description="Reason why the action could not be determined"
    )
    suggested_action: str | None = Field(
        None, description="Suggested action if the intent is partially clear"
    )


class AgentActionSchema(BaseModel):
    """Schema for agent action decision and extracted data."""

    action: ActionType
    create_session_data: CreateSessionData | None = None
    close_session_data: CloseSessionData | None = None
    assign_item_to_user_data: AssignItemToUserData | None = None
    unknown_data: UnknownActionData | None = None
    # Más campos de datos se pueden agregar aquí según las acciones
    # create_invoice_data: CreateInvoiceData | None = None
    # add_user_to_session_data: AddUserToSessionData | None = None

