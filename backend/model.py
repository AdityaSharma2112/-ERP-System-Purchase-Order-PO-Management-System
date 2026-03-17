from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel

class Vendor(SQLModel, table=True):
    __tablename__ = "vendors"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    contact: str = Field(default=None, max_length=100)
    rating: Optional[int] = Field(default=None, ge=1, le=5)

    purchase_orders: List["PurchaseOrder"] = Relationship(back_populates="vendor")

class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    sku: str = Field(index=True, unique=True)
    unit_price: float
    stock_level: int = 0
    description: str
    order_items: List["PurchaseOrderItem"] = Relationship(back_populates="product")

class PurchaseOrder(SQLModel, table=True):
    __tablename__ = "purchase_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    reference_no: str = Field(index=True, unique=True)
    vendor_id: int = Field(foreign_key="vendors.id")
    total_amount: float = 0
    status: str = "Pending"
    vendor: Optional[Vendor] = Relationship(back_populates="purchase_orders")
    items: List["PurchaseOrderItem"] = Relationship(back_populates="purchase_order")

class PurchaseOrderItem(SQLModel, table=True):
    __tablename__ = "purchase_order_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    po_id: int = Field(foreign_key="purchase_orders.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int
    price: float
    purchase_order: Optional[PurchaseOrder] = Relationship(back_populates="items")
    product: Optional[Product] = Relationship(back_populates="order_items")


class PurchaseOrderItemCreate(SQLModel):
    product_id: int
    quantity: int
    price: float

class PurchaseOrderCreate(SQLModel):
    reference_no: str
    vendor_id: int
    status: str = "Pending"
    items: List[PurchaseOrderItemCreate]

class AutoDescription(BaseModel):
    product: str