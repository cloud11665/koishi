import re
import html as libhtml
from datetime import datetime
from functools import lru_cache
from typing import List

import chardet
import requests as rq
import lxml

from models import _HashModel
from models import RStatus
from utils import xpstr

class ResultTest(_HashModel):
	name:str
	status:RStatus
	time:str

class ResultDetails(_HashModel):
	tests:List[ResultTest]
	source:str

	def __repr__(self):
		text = repr(self.source)[1:48]+"..." if len(self.source) > 50 else repr(self.source)
		test_val = [x.status.name for x in self.tests]
		test_val = " ".join(test_val)
		return f"<DetailedResult {test_val} {text}>"

	def __str__(self):
		return repr(self)


class Result:
	def __init__(self, ses:rq.Session, id:int, parent_id:int, src:str, status:RStatus, date:datetime):
		self._ses = ses
		self.id = id
		self.parent_id = parent_id
		self.src = src
		self.status = status
		self.date = date

	@property
	@lru_cache(None)
	def details(self):
		resp = self._ses.get(f"https://satori.tcs.uj.edu.pl/contest/{self.parent_id}/results/{self.id}")
		dom = lxml.html.fromstring(resp.text)

		tests = []
		for tr in dom.xpath("//table[@class='docutils']/tbody[@valign='top']/tr"):
			name = xpstr(tr, r".//td[1]/text()")

			status = xpstr(tr, r".//td[2]/text()")
			status = RStatus[status]

			time = xpstr(tr, r".//td[3]/text()")
			time = re.sub(r"\D+$", "", time)

			tests.append(
				ResultTest(name=name, status=status, time=time)
			)

		source = xpstr(dom, r"//pre[@class='literal-block']/text()")
		source = libhtml.unescape(source)

		return ResultDetails(tests=tests, source=source)

	@property
	def ok(self):
		return not self.status.value

	def __eq__(self, other):
		return self.id == other.id

	def __ne__(self, other):
		return not self.id == other.id

	def __hash__(self):
		return hash(self.id)

	def __repr__(self):
		return f"<Result {self.id} {self.src} {self.date} {self.status.name}>"

	def __str__(self):
		return repr(self)
