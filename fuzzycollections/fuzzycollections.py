from __future__ import absolute_import, division, print_function, unicode_literals

import logging
from collections import defaultdict
from heapq import nsmallest
from itertools import islice
from operator import itemgetter
from typing import TYPE_CHECKING, cast

from genutility.iter import no_dupes

if TYPE_CHECKING:
	from typing import Callable, Dict, Iterable, Iterator, List, Optional, Set, Tuple, Union

	DistanceFuncT = Callable[[str, str], int]
	DistanceFuncMaxT = Callable[[str, str, Optional[int]], int]

class distance_function_class(object):

	__slots__ = ("func", )

	def __init__(self, func):
		# type: (Callable, ) -> None

		self.func = func

class distance_polyleven(distance_function_class):

	def __init__(self):
		# type: () -> None

		try:
			from polyleven import levenshtein as _distance
		except ImportError:
			logging.error("Please pip install polyleven")
			raise

		distance_function_class.__init__(self, _distance)

	def get_func(self, max_distance):
		# type: (bool, ) -> Callable

		if max_distance:
			return self.max_distance
		else:
			return self.func

	def max_distance(self, s1, s2, max_distance=None):
		# type: (str, str, Optional[int]) -> int

		return self.func(s1, s2, max_distance is not None and max_distance or -1)


class distance_jellyfish(distance_function_class):

	def __init__(self):
		# type: () -> None

		try:
			from jellyfish import damerau_levenshtein_distance as _distance
		except ImportError:
			logging.error("Please pip install jellyfish")
			raise

		distance_function_class.__init__(self, _distance)

	def get_func(self, max_distance):
		# type: (bool, ) -> Callable

		if max_distance:
			return self.max_distance
		else:
			return self.func

	def max_distance(self, s1, s2, max_distance=None):
		# type: (str, str, Optional[int]) -> int

		return self.func(s1, s2)


def get_distance_func(func="levenshtein", max_distance=False):
	# type: (Union[str, DistanceFuncT, DistanceFuncMaxT], bool) -> Union[DistanceFuncT, DistanceFuncMaxT]

	if isinstance(func, str):
		if func == "levenshtein":
			return distance_polyleven().get_func(max_distance)

		elif func == "damerau":
			return distance_jellyfish().get_func(max_distance)

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

		for item in items:
			self.append(item)

	def find(self, item, max_distance, limit):
		# type: (str, Optional[int], Optional[int]) -> List[Tuple[int, str]]

		raise NotImplementedError

	def findsorted(self, item, max_distance, limit):
		# type: (str, Optional[int], Optional[int]) -> List[Tuple[int, str]]

		raise NotImplementedError

class LinearCollection(FuzzyCollection):

	def __init__(self, distance_func, preprocess_func=None):
		# type: (Union[str, DistanceFuncMaxT], Callable[[str], str]) -> None

		self.distance_func = cast("DistanceFuncMaxT", get_distance_func(distance_func, max_distance=True))
		self.preprocess_func = get_preprocess_func(preprocess_func)

		self.collection = [] # type: List[str]
		self.mutable = True

	def __len__(self):
		# type: () -> int

		return len(self.collection)

	def append(self, item):
		# type: (str, ) -> None

		if not self.mutable:
			raise RuntimeError()

		self.collection.append(item)

	def remove(self, item):
		# type: (str, ) -> None

		self.collection.remove(item)

	def extend(self, items):
		# type: (Iterable[str], ) -> None

		if not self.mutable:
			raise RuntimeError()

		self.collection.extend(items)

	def _distances(self, query, max_distance=None):
		# type: (str, Optional[int]) -> Iterator[Tuple[int, str]]

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
		# type: (List[str], Union[str, DistanceFuncMaxT], Callable) -> LinearCollection

		""" Returns a LinearCollection which operates on a view of another collection.
			Preprocess is done each time the collection is queried.
			New items cannot be added. They should be added to the original collection.
		"""

		col = LinearCollection(distance_func, preprocess_func)
		col.collection = collection
		col.mutable = False

		return col

class BkCollection(FuzzyCollection):

	def __init__(self, distance_func, max_distance=None):
		# type: (Union[str, DistanceFuncT], Optional[int]) -> None

		from genutility.metrictree import BKTree

		distance_func = cast("DistanceFuncT", get_distance_func(distance_func, max_distance=False))
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

""" Possible optimizations: 
	- keep track of longest word in vocab to exit early when trying to find long words
"""
class SymmetricDeletesCollection(FuzzyCollection):

	def __init__(self, max_distance):
		# type: (int, ) -> None

		self.max_distance = max_distance

		# maps deletes to items
		self.vocab = defaultdict(set) # type: Dict[str, Set[str]]
		self.size = 0

	def __len__(self):
		# type: () -> int

		return self.size

	@classmethod
	def _deletes_it(cls, item, depth):
		# type: (str, int) -> Iterator[str]

		# This should be improved. Return deletes without duplicates and ordered by delete distance

		yield item

		if depth == 0:
			return

		for i in range(len(item)):
			cand = item[:i] + item[i+1:]
			for c in cls._deletes_it(cand, depth - 1):
				yield c

	def _deletes(self, item):
		# type: (str, ) -> Set[str]

		return set(self._deletes_it(item, min(self.max_distance, len(item) - 1)))

	def append(self, item):
		# type: (str, ) -> bool

		if item in self:
			return False

		self.size += 1

		for delete in self._deletes(item):
			self.vocab[delete].add(item)

		return True

	def __contains__(self, item): # fixme: is this really correct?
		# type: (str, ) -> bool

		try:
			return item in self.vocab[item]
		except KeyError:
			return False

	def remove(self, item):
		# type: (str, ) -> bool

		if item not in self:
			return False

		self.size -= 1

		for delete in self._deletes(item):
			# these should never fail because we determined that the item is in the collection already
			s = self.vocab[delete]
			s.remove(item)
			if not s:
				self.vocab.pop(delete)

		return True

	def _find(self, item):
		# type: (str, ) -> Iterator[str]

		for delete in self._deletes(item):
			for candidate in self.vocab.get(delete, ()):
				yield candidate

	def find(self, item):  # type: ignore[override]
		# type: (str, ) -> List[str]

		return list(no_dupes(self._find(item)))

if __name__ == "__main__":
	col = SymmetricDeletesCollection(3)
	col.append("hou")
	#col.append("refrigerator")
	#col.extend(["house", "refrigerator"])

	print(col.vocab)
