from pydantic import BaseModel
from typing import Literal
from pydantic import ValidationError

class Finding(BaseModel):
    file : str
    line : int
    severity : Literal["low", "medium", "high"]
    category : str
    message : str
