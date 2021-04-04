from collections import defaultdict
from enum import Enum

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
	QUE = 10
