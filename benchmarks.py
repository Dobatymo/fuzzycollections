from __future__ import absolute_import, division, print_function, unicode_literals
import tracemalloc
from genutility.time import PrintStatementTime
from fuzzycollections import LinearCollection, BkCollection, SymmetricDeletesCollection

from nltk.corpus import words

w = words.words()

def print_total_memory(name, snapshot1, snapshot2):
	stats = snapshot2.compare_to(snapshot1, 'lineno')
	total = sum(stat.size for stat in stats) / 1024 / 1024
	print("{} uses {:.3f} MiB of memory".format(name, total))

tracemalloc.start()

"""
LinearCollection init took 0.01600000000325963
LinearCollection uses 2.041 MiB of memory
LinearCollection query took 236.21900000004098
BkCollection init took 3.077999999979511
BkCollection uses 67.560 MiB of memory
BkCollection query took 27.45299999997951
SymmetricDeletesCollection init took 15.35999999998603
SymmetricDeletesCollection uses 688.882 MiB of memory
SymmetricDeletesCollection query took 0.031000000017229468
"""

def asd_1(num):
	with PrintStatementTime("LinearCollection init took {delta}"):
		snapshot1 = tracemalloc.take_snapshot()
		a = LinearCollection("levenshtein")
		a.extend(w)
		snapshot2 = tracemalloc.take_snapshot()

	print_total_memory("LinearCollection", snapshot1, snapshot2)

	with PrintStatementTime("LinearCollection query took {delta}"):
		for i in range(num):
			res = a.find("horible", 1) # [(1, 'horrible')]

def asd_2(num):
	with PrintStatementTime("BkCollection init took {delta}"):
		snapshot1 = tracemalloc.take_snapshot()
		a = BkCollection("levenshtein")
		a.extend(w)
		snapshot2 = tracemalloc.take_snapshot()

	print_total_memory("BkCollection", snapshot1, snapshot2)

	with PrintStatementTime("BkCollection query took {delta}"):
		for i in range(num):
			res = a.find("horible", 1) # [(1, 'horrible')]

def asd_3(num):
	with PrintStatementTime("SymmetricDeletesCollection init took {delta}"):
		snapshot1 = tracemalloc.take_snapshot()
		a = SymmetricDeletesCollection(max_distance=1)
		a.extend(w)
		snapshot2 = tracemalloc.take_snapshot()

	print_total_memory("SymmetricDeletesCollection", snapshot1, snapshot2)

	with PrintStatementTime("SymmetricDeletesCollection query took {delta}"):
		for i in range(num):
			res = a.find("horible") # ['horrible']

if __name__ == "__main__":
	TOTAL = 1000

	asd_1(TOTAL)
	asd_2(TOTAL)
	asd_3(TOTAL)
