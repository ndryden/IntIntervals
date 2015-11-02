IntIntervals
============

`IntIntervals` is a Python module for representing disjoint integer intervals in a memory-efficient manner while supporting set operations.

Overview
========

Instead of storing every integer explicitly, `IntIntervals` represents intervals as the starting and ending value `[a, b]`. This provides a large memory reduction in the case of long runs of consecutive integers. `IntIntervals` is intended for cases where storing every integer is an unacceptable memory overhead and involves tradeoffs: some operations are slower than if they were performed on a standard Python set or dictionary. In particular, lookup (`x in s`) now takes logarithmic instead of constant time.

The only class provided is `IntIntervals`, which supports the standard operations a Python `frozenset` supports, plus a few additional operations that have proved useful.

This code is based upon the `Interval` class I originally developed for [PGDB](https://github.com/ndryden/PGDB). It seems that the concept is the same as in a [discrete interval encoding tree](http://web.engr.oregonstate.edu/~erwig/diet/) (diet) augmented with set-theoretic operations, but I wasn't aware of diets when I originally wrote this.

Installation
============

To install, just run the `setup.py` script:
```
python setup.py install
```

Example
=======

```python
import random
from intintervals import IntIntervals

# Generate some random integers.
ints1 = [random.randint(0, 99) for i in range(50)]
ints2 = [random.randint(0, 99) for i in range(50)]

# Create our integer intervals.
intv1 = IntIntervals(ints1)
intv2 = IntIntervals(ints2)

# Look at our intervals.
print intv1
print intv2

# Check membership.
42 in intv1
13 not in intv2

# Set operations.
intv1.union(intv2)
intv1.intersection(intv2)
intv1.difference(intv2)
intv1.symmetric_difference(intv2)
intv1.isdisjoint(intv2)
intv1.issubset(intv2)
intv1.issuperset(intv2)

# Identify the smallest and largest values.
intv1.smallest()
intv1.largest()

# Iterate over every integer in the intervals.
for i in intv1: print i

```

Testing
=======

Currently testing is minimal. The `tests/fuzz.py` script will exercise the `union`, `intersection`, `difference`, and `symmetric_difference` operations with large amounts of random input and verify it using Python's built-in `set`.
