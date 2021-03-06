import re
import html as libhtml
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Optional, Union
from enum import Enum

import chardet
import markdownify as md
import requests as rq
from lxml import etree, html

from models import _HashModel, RStatus, Result


class ResultTest(_HashModel):
	name:str
	status:RStatus
	time:float

class ResultDetails(_HashModel):
	tests:List[ResultTest]
	source:str

	def __repr__(self):
		text = repr(self.source)[1:48]+"..." if len(self.source) > 50 else repr(self.source)
		test_val = [x.status.name for x in self.tests]
		test_val = " ".join(test_val)
		return f"<DetailedResult {test_val} \"{text}\">"

	def __str__(self):
		return repr(self)


class Result:
	def __init__(self, ses:rq.Session, id_:int, parent_id:int, code:str, status:RStatus, date:datetime):
		self.ses = ses
		self.id = id_
		self.parent_id = parent_id
		self.code = code
		self.status = status
		self.date = date

	@property
	@lru_cache(2<<16)
	def details(self):
		resp = self.ses.get(f"https://satori.tcs.uj.edu.pl/contest/{self.parent_id}/results/{self.id}")
		dom = html.fromstring(resp.text)

		tests = []
		for tr in dom.xpath("//table[@class='docutils']/tbody[@valign='top']/tr"):
			name = tr.xpath(".//td[1]/text()")
			name = "".join(name)

			status = tr.xpath(".//td[2]/text()")
			status = "".join(status)
			status = RStatus[status]

			time = tr.xpath(".//td[3]/text()")
			time = "".join(time)
			time = re.sub("\D+$", "", time)

			tests.append(ResultTest(name=name, status=status, time=time))

		source = dom.xpath("//pre[@class='literal-block']/text()")
		source = "".join(source)
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

	def __str__(self):
		return f"{self.code}, {self.status.name}"

	def __repr__(self):
		return f"<Result {self.id} {self.code} {self.date} {self.status.name}>"
