"""Payment matching models for structured outputs."""

from pydantic import BaseModel, Field


class ItemMatch(BaseModel):
    """Schema for matching a paid item.
    
    Represents a single item that the user claims to have paid for.
    """
    
    item_description: str = Field(
        ..., 
        description="Description of the item the user paid for (e.g., 'pizza', 'bebida')"
    )
    quantity: int = Field(
        default=1,
        ge=1,
        description="Quantity of items paid"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence level of the match (0.0 to 1.0)"
    )


class PaymentIntent(BaseModel):
    """Schema for payment intent extraction.
    
    Extracts the user's intent when they say they paid for something
    and uploads a payment proof image.
    """
    
    items_paid: list[ItemMatch] = Field(
        ...,
        min_length=1,
        description="List of items the user claims to have paid for"
    )
    is_payment: bool = Field(
        default=True,
        description="Whether this is actually a payment intent (true) or something else (false)"
    )
    payment_description: str | None = Field(
        default=None,
        description="Optional description or note about the payment"
    )


class ItemPaymentMatch(BaseModel):
    """Schema for matched items from database.
    
    Links the payment intent with actual database items.
    """
    
    item_id: int = Field(..., description="Database ID of the item")
    description: str = Field(..., description="Item description from database")
    unit_price: float = Field(..., gt=0, description="Unit price of the item")
    total_price: float = Field(..., gt=0, description="Total price including tip")
    matched_from_intent: str = Field(
        ..., 
        description="Original item description from user's payment intent"
    )


class PaymentMatchResult(BaseModel):
    """Complete payment matching result.
    
    Contains the matched items and payment analysis.
    """
    
    matched_items: list[ItemPaymentMatch] = Field(
        ...,
        description="Items matched from the database"
    )
    expected_amount: float = Field(
        ...,
        ge=0,
        description="Total expected payment amount (sum of matched items)"
    )
    actual_amount: float = Field(
        ...,
        ge=0,
        description="Actual amount from the transfer/payment proof"
    )
    difference: float = Field(
        ...,
        description="Difference between actual and expected (positive = overpaid, negative = underpaid)"
    )
    payment_status: str = Field(
        ...,
        description="Status: 'exact', 'overpaid', or 'underpaid'"
    )

