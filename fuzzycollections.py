from __future__ import absolute_import, division, print_function, unicode_literals

from builtins import str

import logging
from heapq import nsmallest
from operator import itemgetter
from itertools import islice
from typing import TYPE_CHECKING

from future.utils import PY2

if TYPE_CHECKING:
	from typing import Callable, List, Iterable, Iterator, Tuple, Optional

def get_distance_func(func="levenshtein", max_distance=False):
	# type: (Union[str, Callable], bool) -> Union[Callable[[str, str], int], Callable[[str, str, int], int]]

	if isinstance(func, str):
		if func == "levenshtein":
			if PY2:
				try:
					from Levenshtein import distance as _distance
				except ImportError:
					logging.error("Please pip install python-Levenshtein")
					raise

				if max_distance:
					return lambda s1, s2, max_distance: _distance(s1, s2)
				else:
					return _distance
			else:
				try:
					from polyleven import levenshtein as _distance
				except ImportError:
					logging.error("Please pip install polyleven")
					raise

				return lambda s1, s2, max_distance=None: _distance(s1, s2, max_distance is not None and max_distance or -1)

		elif func == "damerau":
			try:
				from jellyfish import damerau_levenshtein_distance as _distance
			except ImportError:
				logging.error("Please pip install jellyfish")
				raise

			if max_distance:
				return lambda s1, s2, max_distance: _distance(s1, s2)
			else:
				return _distance

		else:
			raise ValueError("Invalid distance function name")

	elif callable(func):
		return func

	else:
		raise ValueError("distance function must be callable or string")

def get_preprocess_func(func=None):
	# type: (Optional[Union[str, Callable[[str], str]]], ) -> Callable[[str], str]

	if func is None:
		return lambda s: s

	elif func == "default":
		return lambda s: s.replace(" ", "").lower()

	elif callable(func):
		return func

	else:
		raise ValueError("preprocess function must be None, 'default' or a callable")

def limitedsort(it, limit=None):
	# type: (Iterable[Tuple[int, str]], Optional[int]) -> List[Tuple[int, str]]

	if limit is None:
		return sorted(it, key=itemgetter(0))
	elif limit >= 0:
		return nsmallest(limit, it, key=itemgetter(0))
	else:
		raise ValueError("limit cannot be negative")

class FuzzyCollection(object):

	def append(self, item):
		# type: (str, ) -> None

		raise NotImplementedError

	def extend(self, items):
		# type: (Iterable[str], ) -> None

		raise NotImplementedError

	def find(self, item, max_distance, limit):
		# type: (str, Optional[int]) -> List[Tuple[int, str]]

		raise NotImplementedError

	def findsorted(self, item, max_distance, limit):
		# type: (str, Optional[int]) -> List[Tuple[int, str]]

		raise NotImplementedError

class LinearCollection(FuzzyCollection):

	def __init__(self, distance_func, preprocess_func=None):
		# type: (Callable[[str, str, int], int], Callable[[str], str]) -> None

		self.distance_func = get_distance_func(distance_func, max_distance=True)
		self.preprocess_func = get_preprocess_func(preprocess_func)

		self.collection = [] # type: List[str]
		self.mutable = True

	def append(self, item):
		# type: (str, ) -> None

		if not self.mutable:
			raise RuntimeError()

		self.collection.append(item)

	def extend(self, items):
		# type: (Iterable[str], ) -> None

		if not self.mutable:
			raise RuntimeError()

		self.collection.extend(items)

	def _distances(self, query, max_distance=None):
		# type: (str, Optional[str]) -> Iterator[Tuple[int, str]]

		query = self.preprocess_func(query)

		for item in self.collection:
			distance = self.distance_func(query, self.preprocess_func(item), max_distance)
			if max_distance is None or distance <= max_distance:
				yield distance, item

	def find(self, item, max_distance=None, limit=None):
		# type: (str, Optional[int], Optional[int]) -> List[Tuple[int, str]]

		return list(islice(self._distances(item, max_distance), limit))

	def findsorted(self, item, max_distance=None, limit=None):
		# type: (str, Optional[int], Optional[int]) -> List[Tuple[int, str]]

		return limitedsort(self._distances(item, max_distance), limit)

	@staticmethod
	def from_view(collection, distance_func, preprocess_func=None):
		# type: (Collection[str], Callable, Callable) -> LinearCollection

		""" Returns a LinearCollection which operates on a view of another collection.
			Preprocess is done each time the collection is queried.
			New items cannot be added. They should be added to the original collection.
		"""

		col = LinearCollection(distance_func, preprocess_func)
		col.collection = collection
		col.mutable = False

		return col

class BkCollection(FuzzyCollection):

	def __init__(self, distance_func):
		# type: (Callable[[str, str], int], Callable[[str], str]) -> None

		from genutility.metrictree import BKTree

		distance_func = get_distance_func(distance_func, max_distance=False)
		self.tree = BKTree(distance_func)

	def append(self, item):
		# type: (str, ) -> None

		self.tree.add(item)

	def extend(self, items):
		# type: (Iterable[str], ) -> None

		self.tree.update(items)

	def find(self, item, max_distance, limit=None):
		# type: (str, int, Optional[int]) -> List[Tuple[int, str]]

		return list(islice(self.tree.find(item, max_distance), limit))

	def findsorted(self, item, max_distance, limit=None):
		# type: (str, int, Optional[int]) -> List[Tuple[int, str]]

		return limitedsort(self.tree.find(item, max_distance), limit)
