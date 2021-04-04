import re
from typing import Dict, List
from urllib.error import HTTPError

import lxml
import lxml.html
import requests

from koishi.contest import Contest
from koishi.models import CStatus, statdict
from koishi.utils import parse_news, xpstr, timed_lru_cache


class Koishi:
	""""""
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
			raise HTTPError(resp.url,resp.status_code, "Internal satori error",
				hdrs={},fp=None)

		if dom.xpath(r"//*[@id='content']/form/table/tr[1]/td/text()='Login failed!'"):
			raise HTTPError(resp.url,resp.status_code, "Invalid login credentials",
				hdrs={},fp=None)

	@timed_lru_cache(7200, None)
	def _get_contests(self) -> List[Contest]:
		resp = self._ses.get("https://satori.tcs.uj.edu.pl/contest/select")
		dom = lxml.html.fromstring(resp.text)

		out = []
		for table in dom.xpath(r"//table[@class='results']"):
			for tr in table.xpath(r".//tr[position()!=1]"):
				id = xpstr(tr, r".//a[@class='stdlink']/@href")
				id = int(re.sub(r"^\/\w+\/|\/$", "", id))

				status = xpstr(tr, r".//td[3]//text()")
				status = CStatus(statdict[status])

				name = xpstr(tr, r".//a[@class='stdlink']/text()")
				desc = xpstr(tr, r".//td[@class='description']/text()")

				out.append(
					Contest(self._ses, id, name, desc, status)
				)

		if len(out) == 1 and out[0].id == 251519:
			raise HTTPError(resp.url,resp.status_code,
				"An error occurred while fetching user's contests",
				hdrs={},fp=None)

		# return [*sorted(out, key=lambda x,y: x.id > y.id)]
		return out

	@timed_lru_cache(7200, None)
	def __get_news(self) -> List[str]:
		resp = self._ses.get(f"https://satori.tcs.uj.edu.pl/news")
		return parse_news(resp.text)

	@property
	def contests(self) -> List[Contest]:
		"""Returns a list of user's contests"""
		return self._get_contests()

	@property
	def news(self) -> List[str]:
		"""Returns a list of Markdown formatted posts"""
		return self.__get_news()

	@property
	def profile(self) -> Dict[str, str]:
		"""Ret"""
		resp = self._ses.get("https://satori.tcs.uj.edu.pl/profile")
		dom = lxml.html.fromstring(resp.text)

		fname = xpstr(dom, r"//input[@id='id_firstname']/@value")
		lname = xpstr(dom, r"//input[@id='id_lastname']/@value")
		affi = xpstr(dom, r"//input[@id='id_affiliation']/@value")

		return {
			"first_name": fname,
			"last_name": lname,
			"affiliation": affi,
		}

	def relog(self) -> bool:
		"""Relogs user with credentials provided in `__init__`"""
		resp = self._ses.post(
			"https://satori.tcs.uj.edu.pl/login",
			files = (
				("login", (None, self.__login)),
				("password", (None, self.__passwd))
			)
		)
		return resp.ok

	def update(self, **fields) -> bool:
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
				hdrs={},fp=None)

		return tuple(self.profile.values()) == (fname, lname, affi)

	def __hash__(self):
		return hash((type(self), self.__login, self.__passwd))

	def __repr__(self):
		return f"<{type(self)} #{hash(self)}>"

	def __str__(self):
		return repr(self)

	def __eq__(self, other):
		return hash(self) == hash(other)

	def __ne__(self, other):
		return hash(self) != hash(other)

	def __getitem__(self, key):
		return self.contests[key]

	def __delitem__(self, key):
		del self.contests[key]

	def __setitem__(self, key, val):
		raise NotImplementedError(
			"Overriding contests is not supported"
		)

	def __len__(self):
		return len(self.contests)

	def __call__(self):
		return self.relog()
