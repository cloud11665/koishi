from pydantic import BaseModel
from enum import Enum
from collections import defaultdict

statdict = defaultdict(lambda:0)
statdict[""] = 1
statdict["Pending"] = 2


class Status(Enum):
	denied = 0
	approved = 1
	pending = 2


class Contest(BaseModel):
	id:int
	name:str
	desc:str
	status:Status