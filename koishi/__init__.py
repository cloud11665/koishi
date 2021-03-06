import re
from datetime import datetime
from functools import lru_cache, singledispatchmethod
from typing import Dict, List, Optional, Union
from urllib.error import HTTPError, URLError

import chardet
from lxml import etree, html
from markdownify import markdownify as markdown
from requests import Session, request

import models as mod
from contest import Contest
from exceptions import AccessError, LoginError


class Koishi:
	def __init__(self, username:str, password:str):
		self.uname = username
		self.passwd = password
		self.ses = Session() # To store the session cookie

		resp = self.ses.post("https://satori.tcs.uj.edu.pl/login",
			data = {
				"login": self.uname,
				"password": self.passwd
			},
			files = [] # To simulate a multipart/data request
			)

		dom = html.fromstring(resp.text)

		if not resp.ok:
			raise HTTPError(resp.url,resp.status_code,"Internal satori error",
				hdrs=None,fp=None)

		if dom.xpath("//*[@id='content']/form/table/tr[1]/td/text()='Login failed!'"):
			raise HTTPError(resp.url,resp.status_code,"Invalid login credentials",
				hdrs=None,fp=None)

		name = dom.xpath("//ul[@class='headerRightUl']/li[1]/text()")
		name = "".join(name).split()[-2:] # "Logged in as {1} {2}" -> ["{1}", "{2}"]
		self.name = name

	@property
	@lru_cache(2<<16)
	def contests(self) -> List[Contest]:
		resp = self.ses.get("https://satori.tcs.uj.edu.pl/contest/select")
		dom = html.fromstring(resp.text)

		out = []
		for table in dom.xpath("//table[@class='results']"):
			for tr in table.xpath(".//tr[position()!=1]"):
				id_ = tr.xpath(".//a[@class='stdlink']/@href")
				id_ = "".join(id_)
				id_ = re.sub("^\/\w+\/|\/$", "", id_)

				name = tr.xpath(".//a[@class='stdlink']/text()")
				name = "".join(name)

				desc = tr.xpath(".//td[@class='description']/text()")
				desc = "".join(desc)

				status = tr.xpath(".//td[3]//text()")
				status = "".join(status)
				status = mod.CStatus(mod.statdict[status])

				out.append(Contest(self.ses,
						id=id_, name=name, desc=desc, status=status
				))

		return out

	@singledispatchmethod
	@lru_cache(2<<16)
	def problems(self, con:Contest):
		if con.status.value != 1:
			raise AccessError(f"account not a member of \"{con.name}\" contest")

		resp = self.ses.get(f"https://satori.tcs.uj.edu.pl/contest/{con.id}/problems")
		dom = html.fromstring(resp.text)

		if resp.status_code == 404:
			raise HTTPError(resp.url,resp.status_code,"Contest not found",
				hdrs=None,fp=None)

		out = []
		for series in zip(
			dom.xpath("//div[@id='content']/h4"),
			dom.xpath("//div[@id='content']/div")
		):
			title_, tasks_ = series

			title = title_.xpath(".//text()")
			title = "".join(title)
			title = re.sub("^\s+|\s+.$|\s*\[\w+\/\w+\]\s*$", "", title)
			# "{1} [show/hide] " -> "{1}"
			# "{1} " -> "{1}"
			# " {1}" -> "{1}"

			tasks = []
			for tr in tasks_.xpath(".//table[@class='results']/tr[position()!=1]"):
				code = tr.xpath(".//td[1]/text()")
				code = "".join(code)

				name = tr.xpath(".//td[2]/a/text()")
				name = "".join(name)

				id_ = tr.xpath(".//td[2]/a/@href")
				id_ = "".join(id_)
				id_ = re.sub("^\/\w+\/\d+\/\w+\/|\/$", "", id_)

				note = tr.xpath(".//*[@class='mainsphinx']/p/em/text()")
				note = "".join(note)

				tasks.append(mod.Problem(
					code=code, id=id_, note=note, name=name, parent_id=con.id
				))

			out.append(mod.ProblemSet(
				title=title, problems=tasks
			))

		return out

	@problems.register
	@lru_cache(2<<10)
	def _(self, con:int):
		con = [x for x in self.contests if x.id == con]
		if con:
			return self.problems(*con)

		raise ValueError("specified id not found")

