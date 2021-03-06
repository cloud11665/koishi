from typing import List, Optional

import markdownify as md
from lxml import etree, html

BASE_URL = "https://satori.tcs.uj.edu.pl"

def parse_news(response: str) -> List[str]:
	dom = html.fromstring(response)
	dom.make_links_absolute(BASE_URL)

	out = []
	for div in dom.xpath("//div[@id='content']/div"):
		for tr in div.xpath(".//table[@class='message']"):
			content = etree.tostring(tr, encoding="unicode", with_tail=False)
			content = md.markdownify(content)
			lines = []
			for line in content.split("\n"):
				if line == "": continue
				if line == "> ": continue
				lines.append(line)

			content = "\n".join(lines)
			out.append(content)

	return out


def xpstr(tree, xpath:str) -> str:
	res = tree.xpath(xpath)
	res = "".join(res)
	return res
