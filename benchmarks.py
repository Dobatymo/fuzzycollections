from __future__ import absolute_import, division, print_function, unicode_literals

from genutility.bench import MeasureMemory
from genutility.time import PrintStatementTime
from nltk.corpus import words

from fuzzycollections import BkCollection, LinearCollection, SymmetricDeletesCollection

w = words.words()

"""
LinearCollection uses 2.040 MiB of memory
LinearCollection init took 0.014999999897554517s
LinearCollection query took 224.71900000004098s
BkCollection uses 67.611 MiB of memory
BkCollection init took 6.187000000150874s
BkCollection query took 31.016000000061467s
SymmetricDeletesCollection uses 688.946 MiB of memory
SymmetricDeletesCollection init took 24.625s
SymmetricDeletesCollection query took 0.0470000000204891s
"""

def asd_1(num):
	with PrintStatementTime("LinearCollection init took {delta}s"):
		with MeasureMemory() as m:
			a = LinearCollection("levenshtein")
			a.extend(w)
		m.print("LinearCollection")

	with PrintStatementTime("LinearCollection query took {delta}"):
		for i in range(num):
			res = a.find("horible", 1)
	assert res == [(1, "horrible")]

def asd_2(num):
	with PrintStatementTime("BkCollection init took {delta}"):
		with MeasureMemory() as m:
			a = BkCollection("levenshtein")
			a.extend(w)
		m.print("BkCollection")

	with PrintStatementTime("BkCollection query took {delta}"):
		for i in range(num):
			res = a.find("horible", 1)
	assert res == [(1, "horrible")]

def asd_3(num):
	with PrintStatementTime("SymmetricDeletesCollection init took {delta}"):
		with MeasureMemory() as m:
			a = SymmetricDeletesCollection(max_distance=1)
			a.extend(w)
		m.print("SymmetricDeletesCollection")

	with PrintStatementTime("SymmetricDeletesCollection query took {delta}"):
		for i in range(num):
			res = a.find("horible")
	assert res == ["horrible"]

if __name__ == "__main__":
	TOTAL = 1000

	asd_1(TOTAL)
	asd_2(TOTAL)
	asd_3(TOTAL)
