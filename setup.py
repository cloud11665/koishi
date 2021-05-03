import setuptools

setuptools.setup(
	name="koishi",
	version="1.1.6",
	description="Python wrapper for the unofficial scraped API of the satori testing system.",
	long_description=open("README.md", "r").read(),
	long_description_content_type="text/markdown",
	author="Cloud11665",
	author_email="Cloud11665@gmail.com",
	url="https://github.com/Cloud11665/koishi",
	packages=setuptools.find_packages(),
	install_requires=open("requirements.txt", "r").readlines(),
	license="MIT",
	keywords=["koishi", "tcs", "jagiellonian-university", "satori"],
	classifiers=[
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9",
		"Programming Language :: Python :: 3.10",
		"Operating System :: OS Independent",
	],
	python_requires=">=3.8" # will test with >=3.6
)