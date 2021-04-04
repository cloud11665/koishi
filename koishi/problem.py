from typing import List, Any, Callable
from datetime import datetime
import time

import requests as rq
import lxml
import lxml.html

from koishi.utils import xpstr
from koishi.models import _HashModel
from koishi.models import RStatus
from koishi.result import Result


class ProblemSet(_HashModel):
	problems:List[Any] # fucking pydantic 'arbitrary_types_allowed' bullshit
	title:str

class Problem:
	"""Wrapper class for satori's problem"""
	def __init__(self, ses:rq.Session, id:int, parent_id:int, code:str, name:str, note:str):
		self._ses = ses
		self.id = id
		self.parent_id = parent_id
		self.code = code
		self.name = name
		self.note = note

	@property
	def pdf_url(self) -> str:
		return f"https://satori.tcs.uj.edu.pl/view/ProblemMapping/{self.parent_id}/statement_files/_pdf/{self.code}.pdf"

	def submit(self, src:str, lang:str, callback:Callable=None) -> int:
		resp = self._ses.post(
			f"https://satori.tcs.uj.edu.pl/contest/{self.parent_id}/submit",
			files = (
				("problem", (None, self.id)),
				("codefile", (f"sent_using_koishilib.{lang}", src))
			)
		)

		dom = lxml.html.fromstring(resp.text)
		tr = dom.xpath(r"//table[@class='results']/tr[2]")[0]
		id = int(xpstr(tr, r".//td[1]/a/text()"))

		date = xpstr(tr, r".//td[3]/text()")
		date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

		status = xpstr(tr, r".//td[@class='status']/div[@class='submitstatus']/div/text()")
		status = RStatus[status]

		if callback:
			while status == RStatus.QUE:
				try:
					cresp = self._ses.get(f"https://satori.tcs.uj.edu.pl/contest/{self.parent_id}/results/{id}")

					cdom = lxml.html.fromstring(cresp.text)

					status = xpstr(cdom, r"//div[@id='content']/table/tr[2]/td[5]/text()")
					status = RStatus[status]

					time.sleep(5)
				except rq.exceptions.ConnectionError:
					... # :) your ratelimits are worthless..

			print(id, self.id, src, status, date)
			res = Result(self._ses, id, self.id, src, status, date)

			return callback(res)

		return id

	def __hash__(self):
		return hash((type(self),) + tuple(self.__dict__.values()))

	def __repr__(self):
		return f"<Problem {self.id} {self.code} {self.name}>"

	def __str__(self):
		return repr(self)

	def __eq__(self, other):
		return self.id == other.id

	def __ne__(self, other):
		return self.id != other.id

	def __call__(self, src:str, lang:str, callback:Callable=None):
		self.submit(src,lang,callback)