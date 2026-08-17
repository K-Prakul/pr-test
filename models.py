from pydantic import BaseModel
from typing import Literal
from pydantic import ValidationError

class Finding(BaseModel):
    file : str
    line : int
    severity : Literal["low", "medium", "high"]
    category : str
    message : str

good = Finding(file="app.py", line=10, severity="high", category="security", message="Hardcoded API key")
print(good)

try:
    bad = Finding(file="app.py", line=10, severity="banana", category="security", message="test")
except ValidationError as e:
    print("Validation failed:")
    print(e)