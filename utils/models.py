from typing import Optional
from dataclasses import dataclass


@dataclass
class ReceiptItem:
    name: str  # Product description
    price: str  # Price to pay (before tax)
    barcode: Optional[str] = None
    tax_type: Optional[str] = None  # Tax category

    # Fields for weighted or quantity-based items
    quantity: Optional[float] = None  # Weight (kg)
    unit_price: Optional[float] = None  # Price per kg
