import re
from datetime import datetime
from functools import lru_cache, singledispatchmethod
from typing import Dict, List, Optional, Union
from urllib.error import HTTPError, URLError

import chardet
import lxml
import markdownify as md
import requests

from models import CStatus, statdict
from contest import Contest
from exceptions import AccessError, LoginError

from utils import xpstr
from utils import parse_news

class Koishi:
	def __init__(self, login:str, password:str):
		self.login = login
		self.passwd = password
		self.ses = requests.Session() # Stores the session cookie

		resp = self.ses.post(
			"https://satori.tcs.uj.edu.pl/login",
			files = (
				("login", (None, self.login)),
				("password", (None, self.passwd))
			)
		)
		dom = lxml.html.fromstring(resp.text)

		if not resp.ok:
			raise HTTPError(resp.url,resp.status_code,"Internal satori error",
				hdrs=None,fp=None)

		if dom.xpath("//*[@id='content']/form/table/tr[1]/td/text()='Login failed!'"):
			raise HTTPError(resp.url,resp.status_code,"Invalid login credentials",
				hdrs=None,fp=None)


	@property
	@lru_cache(None)
	def contests(self) -> List[Contest]:
		resp = self.ses.get("https://satori.tcs.uj.edu.pl/contest/select")
		dom = lxml.html.fromstring(resp.text)

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
				status = CStatus(statdict[status])

				out.append(Contest(self.ses,
						id=id_, name=name, desc=desc, status=status
				))

		return out

	# @problems.register
	# @lru_cache(2<<10)
	# def _(self, con:int):
	# 	con = [x for x in self.contests if x.id == con]
	# 	if con:
	# 		return self.problems(*con)

	# 	raise ValueError("specified id not found")

	@property
	@lru_cache(None)
	def news(self) -> List[str]:
		""""""
		resp = self.ses.get(f"https://satori.tcs.uj.edu.pl/news")
		return parse_news(resp.text)

	@property
	def profile(self) -> Dict[str, str]:
		resp = self.ses.get("https://satori.tcs.uj.edu.pl/profile")
		dom = lxml.html.fromstring(resp.text)

		fname = xpstr(dom, "//input[@id='id_firstname']/@value")
		lname = xpstr(dom, "//input[@id='id_lastname']/@value")
		affi  = xpstr(dom, "//input[@id='id_affiliation']/@value")

		return {
			"first_name": fname,
			"last_name": lname,
			"affiliation": affi,
			}

	def relog(self) -> bool:
		resp = self.ses.post(
			"https://satori.tcs.uj.edu.pl/login",
			files = (
				("login", (None, self.login)),
				("password", (None, self.passwd))
			)
		)
		return resp.ok

	def update(self, **fields) -> None:
		"""Updates user's profile.

		Updates users satori profile with specified keyword arguments.
		When no value is provided, parameter's value will not be updated.

		Args:
			first_name:
				A string representing the new first name of the user.
			last_name:
				A string representing the new last name of the user.
			password:
				A string representing the new password of the user.
			affiliation:
				A string representing the new affiliation of the user.

		Raises:
			urllib.error.HTTPError: An error occurred while updating the profile.
		"""
		fname = self.profile["first_name"]
		lname = self.profile["last_name"]
		affi  = self.profile["affiliation"]

		fname = fields.get("first_name", fname)
		lname = fields.get("last_name", lname)
		affi = fields.get("affiliation", affi)

		newpass = fields.get("password", "")
		oldpass = self.passwd if newpass else ""

		resp = self.ses.post(
			"https://satori.tcs.uj.edu.pl/profile",
			files=(
				("firstname", (None, fname)),
				("lastname", (None, lname)),
				("oldpass", (None, oldpass)),
				("newpass", (None, newpass)),
				("confirm", (None, newpass)),
				("affiliation", (None, affi)),
				("changepass", (None, "change"))
			)
		)

		if not resp.ok:
			raise HTTPError(resp.url,resp.status_code,
				"An error occurred while updating the profile",
				hdrs=None,fp=None)

		return self.profile.values() == [fname, lname, affi]
