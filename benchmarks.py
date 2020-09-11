from __future__ import absolute_import, division, print_function, unicode_literals

from genutility.time import PrintStatementTime
from fuzzycollections import LinearCollection, BkCollection, SymmetricDeletesCollection

from nltk.corpus import words

w = words.words()

with PrintStatementTime():
	a = LinearCollection("levenshtein")
	a.extend(w)

with PrintStatementTime():
	for i in range(1000):
		res = a.find("horible", 1) # [(1, 'horrible')]

with PrintStatementTime():
	a = BkCollection("levenshtein")
	a.extend(w)

with PrintStatementTime():
	for i in range(10000):
		res = a.find("horible", 1) # [(1, 'horrible')]
