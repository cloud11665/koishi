import re
from functools import lru_cache
from typing import Dict, List
from urllib.error import HTTPError, URLError

import chardet
import lxml
import requests

from contest import Contest
from models import CStatus
from models import statdict
from utils import xpstr
from utils import parse_news

class Koishi:
	def __init__(self, login:str, password:str):
		self.__login = login
		self.__passwd = password
		self._ses = requests.Session() # Stores the session cookie

		resp = self._ses.post(
			"https://satori.tcs.uj.edu.pl/login",
			files = (
				("login", (None, self.__login)),
				("password", (None, self.__passwd))
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
		resp = self._ses.get("https://satori.tcs.uj.edu.pl/contest/select")
		dom = lxml.html.fromstring(resp.text)

		out = []
		for table in dom.xpath("//table[@class='results']"):
			for tr in table.xpath(".//tr[position()!=1]"):
				id_ = xpstr(tr, r".//a[@class='stdlink']/@href")
				id_ = re.sub(r"^\/\w+\/|\/$", "", id_)

				status = xpstr(tr, r".//td[3]//text()")
				status = CStatus(statdict[status])

				name = xpstr(tr, r".//a[@class='stdlink']/text()")
				desc = xpstr(tr, r".//td[@class='description']/text()")

				out.append(
					Contest(self._ses, id_, name, desc, status)
				)

		return out

	@property
	@lru_cache(None)
	def news(self) -> List[str]:
		""""""
		resp = self._ses.get(f"https://satori.tcs.uj.edu.pl/news")
		return parse_news(resp.text)

	@property
	def profile(self) -> Dict[str, str]:
		resp = self._ses.get("https://satori.tcs.uj.edu.pl/profile")
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
		resp = self._ses.post(
			"https://satori.tcs.uj.edu.pl/login",
			files = (
				("login", (None, self.__login)),
				("password", (None, self.__passwd))
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
		oldpass = self.__passwd if newpass else ""

		resp = self._ses.post(
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

	def __hash__(self):
			return hash((type(self),) + tuple(self.__dict__.values()))

