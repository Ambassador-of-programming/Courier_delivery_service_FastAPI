from pydantic import BaseModel
from typing import Optional


class BarcodeResponse(BaseModel):
    type: Optional[str] = None
    data: Optional[str] = None
