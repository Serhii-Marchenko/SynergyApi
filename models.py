from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class Send(BaseModel):
    id: int

class User(BaseModel):
    phone: str
    code: int

class Recipient(BaseModel):
    phone: int
    restName: str
    numberOfVisitsFrom: int
    numberOfVisitsTo: int
    dateVisitFrom: date
    dateVisitTo: date
    textMessage: str
    linkImage: str
    textButton: Optional[str] = None
    linkButton: Optional[str] = None
    timeToStartSending: Optional[datetime] = None

class UserPhone(BaseModel):
    phone: int