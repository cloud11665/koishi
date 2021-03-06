from datetime import datetime
from functools import lru_cache, singledispatchmethod
from typing import Dict, List, Optional, Union
from enum import Enum

import chardet
import markdownify as md
import requests as rq
from lxml import etree, html

from result import Result
from models import RStatus, CStatus

class Contest:
	def __init__(self, ses: rq.Session, id: int, name: str, desc: str, status: CStatus):
		self.ses = ses
		self.id = id
		self.name = name
		self.desc = desc
		self.status = status

	@lru_cache(2 << 20)
	def news(self, as_md: Optional[bool] = True) -> List[str]:
		resp = self.ses.get(f"https://satori.tcs.uj.edu.pl/contest/{self.id}/news")
		dom = html.fromstring(resp.text)

		out = []
		for div in dom.xpath("//div[@id='content']/div"):
			for tr in div.xpath(".//table[@class='message']"):
				content = etree.tostring(
					tr, pretty_print=True, encoding="unicode", with_tail=False
				)

				if as_md:
					content = md.markdownify(content)
					lines = []
					for line in content.split("\n"):
						if line == "":
							continue
						if line == "> ":
							continue
						lines.append(line)

					content = "\n".join(lines)

				out.append(content)

		return out

	def results(self, limit: Optional[int] = 64):
		resp = self.ses.get(
			f"https://satori.tcs.uj.edu.pl/contest/{self.id}/results?results_limit={limit}"
		)
		dom = html.fromstring(resp.text)

		out = []
		for tr in dom.xpath("//table[@class='results']/tr[position()!=1]"):
			id_ = tr.xpath(".//td[1]/a/text()")
			id_ = "".join(id_)

			code = tr.xpath(".//td[2]/text()")
			code = "".join(code)

			date = tr.xpath(".//td[3]/text()")
			date = "".join(date)
			date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

			status = tr.xpath(".//td[@class='status']/div[@class='submitstatus']/div/text()")
			status = "".join(status)
			status = RStatus[status]

			out.append(Result(self.ses, id_, self.id, code, status, date))

		return out

	def __repr__(self):
		return f"<Contest {self.id} {self.status.name} \"{self.name}\" >"
