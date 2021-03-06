import re
from datetime import datetime
from typing import List
from functools import lru_cache
from urllib.error import HTTPError

import lxml
import markdownify as md
import requests

from exceptions import AccessError
from models import CStatus, Problem, ProblemSet, RStatus
from result import Result
from utils import parse_news, xpstr


class Contest:
	"""Wrapper class for satori contest.

	Args:
		ses: requests.Session
		id: int
		name: str
		desc: str
		status: CStatus

	Fields:
		Contest.id: int
		Contest.name: str
		Contest.desc: str
		Contest.status: CStatus

	Properties:
		news:
			A list of markdown formatted messages.
		problems:
			A list of problems sorted from oldest to newest.
		result:
			The result of the latest submit.
		results:
			A list of latest results.
	"""
	def __init__(self, ses: requests.Session, id: int, name: str, desc: str, status: CStatus):
		self._ses = ses
		self.id = id
		self.name = name
		self.desc = desc
		self.status = status

	@property
	@lru_cache(None)
	def news(self) -> List[str]:
		"""A list of markdown formatted messages."""
		resp = self.ses.get(f"https://satori.tcs.uj.edu.pl/contest/{self.id}/news")
		return parse_news(resp.text)

	@property
	@lru_cache(None)
	def problems(self) -> List[Problem]:
		"""A list of problems sorted from oldest to newest."""
		if self.status.value > 1:
			raise AccessError(f"account not a member of \"{self.name}\" contest")

		resp = self._ses.get(f"https://satori.tcs.uj.edu.pl/contest/{self.id}/problems")
		dom = lxml.html.fromstring(resp.text)

		if resp.status_code == 404:
			raise HTTPError(resp.url,resp.status_code,"Contest not found",
				hdrs=None,fp=None)

		out = []
		for series in zip(
			dom.xpath("//div[@id='content']/h4"),
			dom.xpath("//div[@id='content']/div")
		):
			title_, tasks_ = series
			title = xpstr(title_, ".//text()")
			title = re.sub("^\s+|\s+.$|\s*\[\w+\/\w+\]\s*$", "", title) # " {} [show/hide]  " -> "{}"

			tasks = []
			for tr in tasks_.xpath(".//table[@class='results']/tr[position()!=1]"):
				code = xpstr(tr, ".//td[1]/text()")
				name = xpstr(tr, ".//td[2]/a/text()")
				note = xpstr(tr, ".//*[@class='mainsphinx']/p/em/text()")
				id_  = xpstr(tr,".//td[2]/a/@href")
				id_  = re.sub("^\/\w+\/\d+\/\w+\/|\/$", "", id_)

				tasks.append(Problem(code=code, id=id_, note=note, name=name, parent_id=self.id))
			out.append(ProblemSet(title=title, problems=tasks))

		return out

	@property
	def result(self) -> Result:
		"""The latest submit result."""
		return self.results[0]

	@property
	def results(self) -> List[Result]:
		"""A list of latest results."""
		resp = self._ses.get(f"https://satori.tcs.uj.edu.pl/contest/{self.id}/results?results_limit=256")
		dom = lxml.html.fromstring(resp.text)

		out = []
		for tr in dom.xpath("//table[@class='results']/tr[position()!=1]"):
			id_ = xpstr(tr, ".//td[1]/a/text()")
			code = xpstr(tr, ".//td[2]/text()")
			date = xpstr(tr, ".//td[3]/text()")
			date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
			status = xpstr(tr, ".//td[@class='status']/div[@class='submitstatus']/div/text()")
			status = RStatus[status]

			out.append(Result(self._ses, id_, self.id, code, status, date))

		return out

	def __repr__(self):
		return f"<Contest {self.id} {self.status.name} \"{self.name}\">"

	def __str__(self):
		return repr(self)

	def __eq__(self, other):
		return self.id == other.id

	def __ne__(self, other):
		return self.id != other.id



"""
2a^2 + 2b^2 + 2c^2 - 2ab - 2ac - 2bc >= 0
(a^2 - 2ab + b^2) + (b^2 - 2bc + c^2) + (a^2 - 2ac + c^2) >= 0
(a-b)^2 + (b-c)^2 + (a-c)^2 >= 0
"""
