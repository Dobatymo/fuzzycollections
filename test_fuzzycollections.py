from __future__ import absolute_import, division, print_function, unicode_literals

from itertools import groupby
from operator import itemgetter

from genutility.test import MyTestCase, parametrize

from fuzzycollections import BkCollection, LinearCollection, SymmetricDeletesCollection


def preprocess(s):
	return s.replace(" ", "").lower()

def sort_after_first(it):
	for k, g in groupby(it, key=itemgetter(0)):
		for i in sorted(g):
			yield i

class CollectionTest(MyTestCase):

	cola1 = LinearCollection.from_view([], "levenshtein")
	cola2 = LinearCollection.from_view(["", "asd", "asd qwe", "ASDF", "ASDF QWE"], "levenshtein")

	colb1 = BkCollection("levenshtein")
	colb2 = BkCollection("levenshtein")
	colb2.extend(["", "asd", "asd qwe", "ASDF", "ASDF QWE"])

	@parametrize((cola1, cola2), (colb1, colb2))
	def test_extract_all(self, col1, col2):
		truth = []
		result = col1.findsorted("asd", max_distance=10, limit=None)
		self.assertEqual(truth, result)

		truth = [(0, "asd"), (3, ""), (4, "ASDF"), (4, "asd qwe"), (8, "ASDF QWE")]
		result = col2.findsorted("asd", max_distance=10, limit=None)
		self.assertEqual(truth, list(sort_after_first(result)))

	@parametrize((cola1, cola2), (colb1, colb2))
	def test_extract_md0(self, col1, col2):
		truth = []
		result = col1.findsorted("asd", max_distance=0, limit=None)
		self.assertEqual(truth, result)

		truth = [(0, "asd")]
		result = col2.findsorted("asd", max_distance=0, limit=None)
		self.assertEqual(truth, result)

	@parametrize((cola1, cola2), (colb1, colb2))
	def test_extract_md1(self, col1, col2):
		truth = []
		result = col1.findsorted("asd", max_distance=1, limit=None)
		self.assertEqual(truth, result)

		truth = [(0, "asd"), ]
		result = col2.findsorted("asd", max_distance=1, limit=None)
		self.assertEqual(truth, result)

	@parametrize((cola1, cola2), (colb1, colb2))
	def test_extract_l0(self, col1, col2):
		truth = []
		result = col1.findsorted("asd", max_distance=10, limit=0)
		self.assertEqual(truth, result)

		truth = []
		result = col2.findsorted("asd", max_distance=10, limit=0)
		self.assertEqual(truth, result)

	@parametrize((cola1, cola2), (colb1, colb2))
	def test_extract_l1(self, col1, col2):
		truth = []
		result = col1.findsorted("asd", max_distance=10, limit=1)
		self.assertEqual(truth, result)

		truth = [(0, "asd")]
		result = col2.findsorted("asd", max_distance=10, limit=1)
		self.assertEqual(truth, result)

	@parametrize((cola1, cola2), (colb1, colb2))
	def test_extract_l2(self, col1, col2):
		truth = []
		result = col1.findsorted("asd", max_distance=10, limit=2)
		self.assertEqual(truth, result)

		truth = [(0, "asd"), (3, "")]
		result = col2.findsorted("asd", max_distance=10, limit=2)
		self.assertEqual(truth, result)

class PPCollectionTest(MyTestCase):

	col1 = LinearCollection.from_view([], "levenshtein", preprocess)
	col2 = LinearCollection.from_view(["", "asd", "asd qwe", "ASDF", "ASDF QWE"], "levenshtein", preprocess)

	def test_extract_all(self):
		truth = []
		result = self.col1.findsorted("asd", max_distance=None, limit=None)
		self.assertEqual(truth, result)

		truth = [(0, "asd"), (1, "ASDF"), (3, ""), (3, "asd qwe"), (4, "ASDF QWE")]
		result = self.col2.findsorted("asd", max_distance=None, limit=None)
		self.assertEqual(truth, result)

	def test_extract_md0(self):
		truth = []
		result = self.col1.findsorted("asd", max_distance=0, limit=None)
		self.assertEqual(truth, result)

		truth = [(0, "asd")]
		result = self.col2.findsorted("asd", max_distance=0, limit=None)
		self.assertEqual(truth, result)

	def test_extract_md1(self):
		truth = []
		result = self.col1.findsorted("asd", max_distance=1, limit=None)
		self.assertEqual(truth, result)

		truth = [(0, "asd"), (1, "ASDF")]
		result = self.col2.findsorted("asd", max_distance=1, limit=None)
		self.assertEqual(truth, result)

	def test_extract_l0(self):
		truth = []
		result = self.col1.findsorted("asd", max_distance=None, limit=0)
		self.assertEqual(truth, result)

		truth = []
		result = self.col2.findsorted("asd", max_distance=None, limit=0)
		self.assertEqual(truth, result)

	def test_extract_l1(self):
		truth = []
		result = self.col1.findsorted("asd", max_distance=None, limit=1)
		self.assertEqual(truth, result)

		truth = [(0, "asd")]
		result = self.col2.findsorted("asd", max_distance=None, limit=1)
		self.assertEqual(truth, result)

	def test_extract_l2(self):
		truth = []
		result = self.col1.findsorted("asd", max_distance=None, limit=2)
		self.assertEqual(truth, result)

		truth = [(0, "asd"), (1, "ASDF")]
		result = self.col2.findsorted("asd", max_distance=None, limit=2)
		self.assertEqual(truth, result)

class SymmetricDeletesCollectionTest(MyTestCase):

	col = SymmetricDeletesCollection(2)
	col.extend(["house", "refrigerator", "x"])

	@parametrize(
		("house", ["house"]),
		("houe", ["house"]),
		("hou", ["house"]),
		("ho", []),
		("housea", ["house"]),
		("houseaa", ["house"]),
		("houseaaa", []),
		("houea", ["house"]),
	)
	def test_find(self, item, truth):
		result = self.col.find(item)
		self.assertEqual(truth, result)

	@parametrize(
		("house", True),
		("refrigerator", True),
		("x", True),
		("", False),
		("h", False),
		("hous", False),
		("efrigerator", False),
		("housea", False),
		("refrigeratora", False),
	)
	def test_contains(self, item, truth):
		self.assertEqual(truth, item in self.col)

if __name__ == "__main__":
	import unittest
	unittest.main()
