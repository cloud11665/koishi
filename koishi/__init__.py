import re
from functools import lru_cache
from typing import Dict, List
from urllib.error import HTTPError

from lxml import etree, html
from requests import Session, request

#from cred import login
from exceptions import LoginError
from models import Contest, Status, statdict


class Koishi:
	def __init__(self, username:str, password:str):
		self.uname = username
		self.passwd = password
		self.ses = Session()

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

		if dom.xpath("//div[@id='content']/form/table/tr[1]/td/text()='Login failed!'"):
			raise LoginError("Invalid credentials")

		name = dom.xpath("//ul[@class='headerRightUl']/li[1]/text()")
		name = name[0].split()[-2:] # ["Logged in as {1} {2}"] -> ["{1}", "{2}"]
		self.name = name

	@property
	@lru_cache(2<<10)
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
				status = Status(statdict[status])

				out.append(Contest(
						id=id_, name=name, desc=desc, status=status
				))

		return out

# 	@lru_cache(2<<10)
# 	def problems(self, contest:Contest):
# 		raise PermissionError()
# 		...
