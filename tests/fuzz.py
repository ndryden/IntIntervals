"""Lazy testing: fuzz the damn thing."""

from __future__ import print_function
import random
from intintervals import IntIntervals

num_trials = 10000

def _gen_random_ints(a=0, b=999, num=700):
    """Generate num random integers between a and b (inclusive)."""
    return [random.randint(a, b) for i in range(num)]

def _check_same(a, b):
    """Check whether all elements are the same and in the same order."""
    return all([i == j for i, j in zip(a, sorted(list(b)))])

def _do_check(a, b, intvres, setres, op):
    """Check whether intvres and setres agree."""
    if not _check_same(intvres, setres):
        print('ERROR {0}'.format(op))
        print(a)
        print('with')
        print(b)
        print('Expected')
        print(IntIntervals(list(setres)))
        print('got')
        print(intvres)
        return False
    return True

if __name__ == '__main__':
    for trial in range(num_trials):
        ints1 = _gen_random_ints()
        ints2 = _gen_random_ints()
        intervals1 = IntIntervals(ints1)
        intervals2 = IntIntervals(ints2)
        set1 = set(ints1)
        set2 = set(ints2)
        intv_union = intervals1.union(intervals2)
        set_union = set1.union(set2)
        if not _do_check(intervals1, intervals2, intv_union,
                         set_union, 'union'):
            break
        intv_intersection = intervals1.intersection(intervals2)
        set_intersection = set1.intersection(set2)
        if not _do_check(intervals1, intervals2, intv_intersection,
                         set_intersection, 'intersection'):
            break
        intv_difference = intervals1.difference(intervals2)
        set_difference = set1.difference(set2)
        if not _do_check(intervals1, intervals2, intv_difference,
                         set_difference, 'difference'):
            break
        intv_symdiff = intervals1.symmetric_difference(intervals2)
        set_symdiff = set1.symmetric_difference(set2)
        if not _do_check(intervals1, intervals2, intv_symdiff,
                         set_symdiff, 'symmetric difference'):
            break
