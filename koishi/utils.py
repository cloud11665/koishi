from datetime import datetime, timedelta
from functools import lru_cache, wraps
from typing import List, Union

import markdownify as md
from lxml import etree, html

BASE_URL = "https://satori.tcs.uj.edu.pl"

def parse_news(response: str) -> List[str]:
	dom = html.fromstring(response)
	dom.make_links_absolute(BASE_URL)

	out = []
	for div in dom.xpath(r"//div[@id='content']/div"):
		for tr in div.xpath(r".//table[@class='message']"):
			content = etree.tostring(tr, encoding="unicode", with_tail=False)
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


def xpstr(tree, xpath:str) -> str:
	res = tree.xpath(xpath)
	res = "".join(res)
	return res


def timed_lru_cache(seconds:int=60, maxsize:Union[int,None]=128):
	def wrapper_cache(func):
		func = lru_cache(maxsize=maxsize)(func)
		setattr(func, "lifetime_", timedelta(seconds=seconds))
		setattr(func, "expiration_", datetime.utcnow() + getattr(func, "lifetime_"))

		@wraps(func)
		def wrapped_func(*args, **kwargs):
			if datetime.utcnow() >= getattr(func, "expiration_"):
				func.cache_clear()
				setattr(func, "expiration_", datetime.utcnow() + getattr(func, "lifetime_"))
			return func(*args, **kwargs)

		return wrapped_func

	return wrapper_cache

