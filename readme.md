# fuzzycollections

Find values in a collection which are similar according to some distance function.

## Install

- `pip install fuzzycollections[all]` to install with all dependencies. If installed without dependencies, the requirements will depend on which collection class is used.

## Collections

- `BkCollection`: Uses a BK-Tree to find similar matches quickly. Requires a real mathematical metric as distance function.
- `LinearCollection`: Simply uses a linear search through all collection items to find close matches. Distance function can be anything.
