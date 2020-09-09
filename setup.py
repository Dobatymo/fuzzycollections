from setuptools import setup
from io import open

with open("readme.md", "r", encoding="utf-8") as fr:
	long_description = fr.read()

extras_require = {
	"all": [
		"genutility"
		"jellyfish"
		"polyleven; python_version>='3'",
		"python-Levenshtein; python_version<'3'",
	],
}

setup(
	author="Dobatymo",
	name="fuzzycollections",
	version="0.0.1",
	url="https://github.com/Dobatymo/fuzzycollections",
	description="fuzzy collections",
	long_description=long_description,
	long_description_content_type="text/markdown",
	classifiers=[
		"Intended Audience :: Developers",
		"License :: OSI Approved :: ISC License (ISCL)",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 3",
	],
	py_modules=["fuzzycollections"],
	python_requires=">=2.7",
	install_requires=["future"],
	extras_require=extras_require,
	use_2to3=False
)
