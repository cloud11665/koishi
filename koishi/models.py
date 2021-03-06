from collections import defaultdict
from enum import Enum
from datetime import datetime
from typing import List

from pydantic import BaseModel


class _HashModel(BaseModel):
    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))

# Contests

statdict = defaultdict(lambda:2)
statdict[""] = 0
statdict["Pending"] = 1

class CStatus(Enum):
	approved = 0
	denied = 2
	pending = 1

# Problems

class Problem(_HashModel):
	id:int
	parent_id:int
	code:str
	name:str
	note:str

class ProblemSet(_HashModel):
	problems:List[Problem]
	title:str

# Results

class RStatus(Enum):
	OK = 0
	ANS = 1
	TLE = 2
	RTE = 3
	MEM = 4
	EXT = 5
	CME = 6
	INT = 7
	REJ = 8
	RUL = 9

class Result(_HashModel):
	id:int
	parent_id:int
	code:str
	status:RStatus
	date:datetime
