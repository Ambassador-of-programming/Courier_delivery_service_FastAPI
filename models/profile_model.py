from pydantic import BaseModel
from typing import List, Optional, Union
from typing import Dict, Any
from datetime import datetime
from decimal import Decimal


# Модели данных
class ProductCreate(BaseModel):
    package_name: str
    package_barcode: str
    package_quantity: int

class ProductResponse(ProductCreate):
    product_id: int

class OrderCreate(BaseModel):
    customer_name: str
    address: str
    phone: str
    comment: Optional[str] = None
    source: Optional[str] = None
    mp_order_number: Optional[str] = None
    order_total: Union[float, int]
    payment_amount: Union[float, int]
    lift_fee: Union[float, int]
    qr_code: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_name": "Иван Иванов",
                "address": "ул. Пушкина, д. 10, кв. 5",
                "phone": "+79001234567",
                "comment": "Позвонить за час до доставки",
                "source": "веб-сайт",
                "mp_order_number": "WEB-12345",
                "order_total": 1500.50,
                "payment_amount": 1500,
                "lift_fee": 0,
                "qr_code": "QR-67890"
            }
        }

class OrderResponse(OrderCreate):
    order_id: int

class OrderItem(BaseModel):
    product_id: int

class OrderWithItems(OrderResponse):
    items: List[ProductResponse]

class CourierOrderResponse(BaseModel):
    courier_id: int
    order_id: int
    customer_name: str
    address: str
    phone: str

class DeliveredOrderResponse(BaseModel):
    order_id: int
    courier_id: int
    delivery_time: datetime
    customer_name: str
    address: str
    phone: str
    order_total: float  # Изменено с Decimal на float


class UndeliveredOrderResponse(BaseModel):
    order_id: int
    courier_id: int
    delivery_time: datetime
    reason: str
    customer_name: str
    address: str
    phone: str
    order_total: float  # Изменено с Decimal на float

 
