from pydantic import BaseModel,Field
from typing import List,Optional
class ItemDetail(BaseModel):
    item_id: int
    item_name: str
    quantity: int
    price_per_unit: float
    total_price: float
class InvoiceReport(BaseModel):
    store_from: Optional[str]
    store_to: Optional[str]
    action_type: str  # purchase | update | transfer | add | status
    items: List[ItemDetail]
    total_amount: float
    remarks: Optional[str]

from langchain_core.messages import HumanMessage
from langchain.output_parsers import PydanticOutputParser
parser=PydanticOutputParser(pydantic_object=InvoiceReport)
