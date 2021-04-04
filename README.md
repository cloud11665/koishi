<div>
	<h1 align="center">koishi.py</h1>
	<h3 align="center">
		<a href="./README.md">
			<img src="https://raw.githubusercontent.com/Cloud11665/koishi/master/static/logo.svg" height="225">
	 </h3>
	<p align="center">
		<a href="https://pypi.org/project/koishi" target="_blank">
			<img src="https://img.shields.io/pypi/v/koishi?color=8FDB71&label=PyPI&logo=pypi&logoColor=ffffff" alt="pypi version" height="23">
		</a>
		<a href="https://satori.tcs.uj.edu.pl">
			<img src="https://img.shields.io/website?down_color=FF033E&down_message=offline&label=host&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAAHwAAACACAMAAAD%2BkP3uAAAAw1BMVEUAAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2FAAD%2B%2Fv79%2Ff3%2FAAD9%2Ff3%2FAAD9%2FPz9%2Ff3%2B%2Fv7%2FAAD%2F%2F%2F9a2dU2AAAAPHRSTlMAAgMHCQ4QEhQdHyIlJig1Nzg6PFBRU2Zob3F1f4KFkJKXmqSprrC0tbu8w8XP2tvm6Ozt9PX3%2FP39%2Fv7RRkGgAAACQElEQVR42u3ZhXLjQBCE4QnnmJmZGXWG7fd%2FqePbU025Nu3WZJNY%2Bxfbkj4x2hEKAIxr9%2FmzC5JQsln%2BZkrp%2BdJ8AQBofvPDJDE8DwA0f%2FUXvTSPggCw%2FNqbyV98kp6fl3Bdv5T%2BN5ncWpN0L4DkX076enq6relQ9PPJ9dDq6Y88PjllEi%2FoJ7vkO2e19Ht9tvu14PfNKum7n3v2uxcPbl85bVZLv9mzX2yYELxA45vvJ9l%2BvcOLrFDEb2R68v6EiYmLfvzT5J%2F9%2Baxqq4v%2BJC93d8n0JPxyyl2zKJy8%2BG297f7Zd2xQAn43L%2FeDtaWxgfiZLtvr0pJyty4L%2F1l%2FNdnDBoo2FgsUfj1luwCQeCa4oY99nBA2UMa1W3V7TCw3tSxCF1l7kYFhffk2n85mwFcQCXZgY8W9jjHhEB9BlYo4xoojHgcIm8WFRV3%2BhtDfV%2Bg2wN6XeHwY7yTeDrjC%2BekRtsN1H%2F14O%2BOBlRYF3o7GQdg6rtsVcfY5PBZ1dl3cHL1YUa8z6qvK%2FcaFR9EwXJjJCrgb0qrj7gIajws1XOxQ4g1veDvOG97whks1vOHtqrYyeMMb3vB2PW94wwHgQHGAxyG9LiziEHAcEtxGhePw48U8zudsBYeKY5S4tyvjOCy4VcYRgkPAvT0eHM6uiSMKR062Q3Hd1j%2BbQrPLg4TiIGwWh4ukeRwgJkXp7NAQY%2BScVcKFGZVwnY7Hlae9GBsCHYEPesbV7YjHa9U2Xdb9vccyKQrNxclCmhuv25j6AfBL4h4Fn62iAAAAAElFTkSuQmCC&up_color=8FDB71&up_message=online&url=https%3A%2F%2Fsatori.tcs.uj.edu.pl" alt="API endpoint coverage" height="23">
		</a>
		<a href="https://www.codefactor.io/repository/github/cloud11665/koishi">
			<img src="https://img.shields.io/codefactor/grade/github/Cloud11665/koishi?color=8FDB71&logo=CodeFactor&logoColor=ffffff" alt="CodeFactor" height="23">
		</a>
	</p>
	<h2></h2>
	<h3>
		<p align="center">
			<a href="./DOCS.md">[Documentation]</a>
			&nbsp;
			<a href="#installation">[Installation]</a>
			&nbsp;
			<a href="#testing">[Testing]</a>
			&nbsp;
			<a href="#Credits">[Credits]</a>
			&nbsp;
			<a href="#Contributing">[Contributing]</a>
			&nbsp;
			<a href="#License">[License]</a>
		</p>
	</h3>
	<h2></h2>
	<p>&nbsp;</p>
	<p align="center" style="font-size:20;">
		<strong>
			Wrapper library for the unofficial scraped API of the satori testing system.
		</strong>
	</p>
	<p>&nbsp;</p>
	<p>&nbsp;</p>
</div>



## Example usage

```py
>>> from koishi import Koishi
>>> foo = Koishi("login", "password")

>>> foo[4]
<Contest 6460771 approved "Liga Informatyczna V LO, 2020/21">

>>> foo[4].problems
[<Problem 6629872 X1 Promocja>, <Problem 6629900 X2 Magazyn Prezentow>,
...
<Problem 6473321 PIZ Pizza>, <Problem 6473327 TRA Tramwaje>]

>>> foo[4][6]
<Problem 6501411 A01 Meteory>

>>> foo[4][6].submit("print(\"hehe\")", "py")
6851966

>>> foo[4].result
<Result 6851966 A01 2021-04-03 22:45:10 QUE>

>>> foo[4][6].submit("print(\"trolling\")",
...     lang="py",
...     callback=lambda x: print(x.src x.details.tests, sep="\n")
... )
print("trolling")
[ResultTest(name='0', status=<RStatus.ANS: 1>, time='0.004')]
```

## installation
```bash
$ pip install koishi
```

## Credits
- [MasFlam/SatoriCLI.jl](https://github.com/MasFlam/SatoriCLI.jl) - for helping with multipart problem submit requests.
- [zielmicha/satori-cli](https://github.com/zielmicha/satori-cli) - for inspiration / idea.
- [u/plasticparakeet](https://www.reddit.com/r/touhou/comments/9jkphu/windows_characters_as_flatstyle_sprites) - Koishi Komeiji icon.
&nbsp;

## Contributing
1. [Fork](https://github.com/Cloud11665/koishi/fork) this repo
2. Create your feature branch ( `git checkout -b feature/foobar` )
3. Commit your changes &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ( `git commit -am 'Add some foobar'` )
4. Push to the branch &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ( `git push origin feature/foobar` )
5. Create a new Pull Request
&nbsp;

## License
<div align="center">
	<a href="./LICENSE">
		<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/MIT_logo.svg/220px-MIT_logo.svg.png" height="60">
	</a>
</div>

koishi is Free Software: You can use, study share and improve it at your will. Specifically you can redistribute and/or modify it under the terms and conditions of the MIT license.