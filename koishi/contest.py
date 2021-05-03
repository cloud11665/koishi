import re
from datetime import datetime
from functools import lru_cache
from itertools import chain
from typing import List
from urllib.error import HTTPError

import lxml
import lxml.html
import requests

from koishi.exceptions import AccessError
from koishi.models import CStatus, RStatus
from koishi.problem import Problem, ProblemSet
from koishi.result import Result
from koishi.utils import parse_news, xpstr, timed_lru_cache


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

	@timed_lru_cache(7200, None)
	def __get_news(self) -> List[str]:
		resp = self._ses.get(f"https://satori.tcs.uj.edu.pl/contest/{self.id}/news")
		return parse_news(resp.text)

	@timed_lru_cache(7200, None)
	def __get_problemsets(self) -> List[ProblemSet]:
		if self.status.value > 1:
			raise AccessError(f"account not a member of \"{self.name}\" contest")

		resp = self._ses.get(f"https://satori.tcs.uj.edu.pl/contest/{self.id}/problems")
		dom = lxml.html.fromstring(resp.text)

		if resp.status_code == 404:
			raise HTTPError(resp.url,resp.status_code,"Contest not found",
				hdrs={},fp=None)

		out = []
		for series in zip(
			dom.xpath(r"//div[@id='content']/h4"),
			dom.xpath(r"//div[@id='content']/div")
		):
			title_, tasks_ = series
			title = xpstr(title_, ".//text()")
			title = re.sub(r"^\s+|\s+.$|\s*\[\w+\/\w+\]\s*$", "", title) # " {} [show/hide]  " -> "{}"

			tasks = []
			for tr in tasks_.xpath(r".//table[@class='results']/tr[position()!=1]"):
				code = xpstr(tr, r".//td[1]/text()")
				name = xpstr(tr, r".//td[2]/a/text()")
				note = xpstr(tr, r".//*[@class='mainsphinx']/p/em/text()")
				id  = xpstr(tr, r".//td[2]/a/@href")
				id  = re.sub(r"^\/\w+\/\d+\/\w+\/|\/$", "", id)

				tasks.append(
					Problem(self._ses, code=code, id=id, note=note, name=name, parent_id=self.id)
				)

			out.append(
				ProblemSet(title=title, problems=tasks)
			)

		return out


	@property
	def news(self) -> List[str]:
		"""A list of markdown formatted messages."""
		return self.__get_news()

	@property
	def problemsets(self) -> List[ProblemSet]:
		"""A list of ProblemSet objects sorted from oldest to newest"""
		return self.__get_problemsets()

	@property
	def problems(self) -> List[Problem]:
		"""A list of problems  sorted from oldest to newest"""
		return [*chain(*[x.problems for x in self.problemsets])]

	@property
	def result(self) -> Result:
		"""The latest submit result."""
		return self.results[0]

	@property
	def results(self) -> List[Result]:
		"""A list of latest results."""
		resp = self._ses.get(f"https://satori.tcs.uj.edu.pl/contest/{self.id}/results?results_limit=4096")
		dom = lxml.html.fromstring(resp.text)

		out = []
		for tr in dom.xpath(r"//table[@class='results']/tr[position()!=1]"):
			id = xpstr(tr, r".//td[1]/a/text()")
			id = int(id)
			src = xpstr(tr, r".//td[2]/text()")

			date = xpstr(tr, r".//td[3]/text()")
			date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

			status = xpstr(tr, r".//td[@class='status']/div[@class='submitstatus']/div/text()")
			status = RStatus[status]

			out.append(
				Result(self._ses, id, self.id, src, status, date)
			)

		return out

	def __hash__(self):
			return hash((type(self), self.id))

	def __repr__(self):
		return f"<Contest {self.id} {self.status.name} \"{self.name}\">"

	def __str__(self):
		return repr(self)

	def __eq__(self, other):
		return self.id == other.id

	def __ne__(self, other):
		return self.id != other.id

	def __getitem__(self, key):
		return self.problems[key]

	def __delitem__(self, key):
		del self.problems[key]

	def __setitem__(self, key, val):
		raise NotImplementedError(
			"Overriding problems is not supported"
		)

