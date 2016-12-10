from builtins import range

"""Represent disjoint integer-valued intervals."""

_empty_list = list()


class IntIntervals(object):
    """Represent a set of disjoint integer-valued intervals with set operations.

    This attempts to compress contiguous intervals for greater memory
    efficiency by maintaining the invariant that all intervals are maximal.

    Memory usage in the worst case is O(n) where n is the number of integers
    being stored. More generally, it is O(m) where m is the number of disjoint
    intervals present.

    """

    def __init__(self, src=_empty_list, is_sorted=False, is_end_inclusive=True):
        """Create new intervals.

        :param src: what to create the intervals from. One of the following:
        - an int
        - a list of integers
        - a list of tuples (a, b) representing disjoint intervals
        - another IntIntervals object
        :param is_sorted: indicates whether list arguments are already sorted.
        :param is_end_inclusive: indicates whether last values in tuples are inclusive

        If the data is sorted, this is O(n) in the number of inputs; otherwise
        it is O(n logn) due to the sorting.
        """

        if isinstance(src, int):
            self.intervals = [(src, src)]
            return
        elif isinstance(src, IntIntervals):
            self.intervals = src.intervals
            return
        elif not isinstance(src, list):
            raise ValueError('Invalid input')
        self.intervals = []
        if not src:
            return  # Empty, nothing to do.
        list_of_ints = False
        if isinstance(src[0], int):
            src = list(set(src))  # Remove duplicates.
            list_of_ints = True
        elif not isinstance(src[0], tuple):
            raise ValueError('List input does not contain ints or tuples')
        if not is_sorted:
            if list_of_ints:
                src.sort()
            else:
                src.sort(key=lambda x: x[0])
        if list_of_ints:
            # Construct maximal intervals from integers.
            cur_left = src[0]
            cur_right = src[0]
            for i in src[1:]:
                if i == cur_right + 1:
                    cur_right += 1  # Extend current interval.
                else:
                    self.intervals.append((cur_left, cur_right))
                    cur_left = i
                    cur_right = i
            self.intervals.append((cur_left, cur_right))
        else:
            def opt_inclusive(start, end):
                if is_end_inclusive or start == end:
                    return start, end

                return start, end - 1

            # Already have disjoint intervals, but may not be maximal.
            cur_intv = opt_inclusive(*src[0])

            for interval in src[1:]:
                interval = opt_inclusive(*interval)

                if interval[0] == cur_intv[1] + 1:
                    # Intervals are contiguous.
                    cur_intv = (cur_intv[0], interval[1])
                else:
                    self.intervals.append(cur_intv)
                    cur_intv = interval
            self.intervals.append(cur_intv)

    # Internal methods.

    def _binary_search(self, i):
        """Return the index of the interval containing i.

        Returns the interval's index, or None if not found.

        """
        lo = 0
        hi = len(self.intervals)
        while lo < hi:
            mid = (lo + hi) // 2
            v = self.intervals[mid]
            if i < v[0]:
                hi = mid
            elif i > v[1]:
                lo = mid + 1
            else:
                return mid
        return None

    @staticmethod
    def _check_intersect(intv1, intv2):
        """Return True if intv1 and intv2 have a non-empty intersection."""
        return intv1[0] <= intv2[1] and intv2[0] <= intv1[1]

    @staticmethod
    def _interval_intersect(intv1, intv2):
        """Return the intersection (if any) of intv1 and intv2."""
        if IntIntervals._check_intersect(intv1, intv2):
            return (max(intv1[0], intv2[0]), min(intv1[1], intv2[1]))
        else:
            return None

    @staticmethod
    def _interval_difference(intv1, intv2):
        """Return the set-theoretic difference of intv1 and intv2.

        This returns a list containing zero, one, or two intervals.

        """
        if IntIntervals._check_intersect(intv1, intv2):
            if intv1[0] < intv2[0]:
                if intv1[1] <= intv2[1]:
                    return [(intv1[0], intv2[0] - 1)]
                else:
                    return [(intv1[0], intv2[0] - 1),
                            (intv2[1] + 1, intv1[1])]
            else:
                if intv1[1] <= intv2[1]:
                    return []
                else:
                    return [(intv2[1] + 1, intv1[1])]
        else:
            return []

    @staticmethod
    def _merge_intervals(intv1, intv2):
        """Return the union of intv1 and intv2 assuming they intersect."""
        return (min(intv1[0], intv2[0]), max(intv1[1], intv2[1]))

    # External methods.

    def __contains__(self, i):
        """Check whether i is contained in the intervals.

        Check is done in O(log n) time where n is the number of intervals.

        """
        return self._binary_search(i) is not None

    def __len__(self):
        """Return the number of values represented by the intervals."""
        return sum([interval[1] - interval[0] + 1 for interval in self.intervals])

    def __iter__(self):
        """Support iteration over all entries within the intervals."""
        for interval in self.intervals:
            for i in range(interval[0], interval[1]+1):
                yield i

    def __eq__(self, other):
        """Return whether two IntIntervals are the same."""
        if not isinstance(other, IntIntervals):
            return NotImplemented
        return all([x == y for x, y in zip(self.intervals, other.intervals)])

    def __ne__(self, other):
        """Return whether two IntIntervals are not the same."""
        if not isinstance(other, IntIntervals):
            return NotImplemented
        return not self.__eq__(other)

    def isdisjoint(self, other):
        """Return whether this and other and disjoint."""
        return not self.intersection(other)

    def issubset(self, other):
        """Return whether this is a subset of other."""
        return self.union(other) == other

    def __le__(self, other):
        """Return whether this is a subset of other."""
        return self.issubset(other)

    def __lt__(self, other):
        """Return whether this is a strict subset of other."""
        return self.issubset(other) and self != other

    def issuperset(self, other):
        """Return whether this is a superset of other."""
        return self.union(other) == self

    def __ge__(self, other):
        """Return whether this is a superset of other."""
        return self.issuperset(other)

    def __gt__(self, other):
        """Return whether this is a strict superset of other."""
        return self.issuperset(other) and self != other

    def feather(self, amount, inplace=False):
        """
        Will feather each interval by `amount` and return result
        :param amount: integer of number to feather intervals
        :param inplace: (optional) set to true to modify `self` instead of
        returning a copy

        :return: feathered results
        """
        feather = IntIntervals([(start - amount, end + amount)
                                for start, end in self.intervals], is_sorted=True)

        if inplace:
            self.intervals = feather.intervals
            return self

        return feather

    def union(self, other, inplace=False):
        """
        Return the union of `self` with `other`.

        Works in O(n) time where n is the number of intervals in both
        IntIntervals.

        :param other: other IntInterval with which to union against
        :param inplace: (optional) set to True to return an updated `self` and
                        not a copy
        :return: union of `self` and `other`
        """
        if not self:
            if inplace:
                self.intervals = other.intervals[:]
                return self

            return other.copy()
        if not other:
            if inplace:
                return self

            return self.copy()

        union = []
        # top is the current set of intervals we draw from to attempt to extend.
        i = 0  # Index into top.
        j = 1  # Index into bottom.
        # Begin with the left-most interval.
        if self.smallest() < other.smallest():
            cur_interval = self.intervals[0]
            top = other.intervals
            bottom = self.intervals
        else:
            cur_interval = other.intervals[0]
            top = self.intervals
            bottom = other.intervals
        while i < len(top) or j < len(bottom):
            # Check if there is overlap.
            if i < len(top) and top[i][0] <= cur_interval[1]:
                if top[i][1] > cur_interval[1]:
                    cur_interval = (cur_interval[0], top[i][1])
                    i += 1
                    top, bottom = bottom, top
                    i, j = j, i
                else:
                    i += 1
            else:
                union.append(cur_interval)
                # Select the next left-most interval to be the current one.
                if i < len(top):
                    if j < len(bottom):
                        if top[i][0] <= bottom[j][0]:
                            cur_interval = top[i]
                            i += 1
                            top, bottom = bottom, top
                            i, j = j, i
                        else:
                            cur_interval = bottom[j]
                            j += 1
                    else:
                        cur_interval = top[i]
                        i += 1
                elif j < len(bottom):
                    # Only bottom intervals left.
                    cur_interval = bottom[j]
                    j += 1
                else:
                    # No intervals left.
                    cur_interval = None
        if cur_interval is not None:
            union.append(cur_interval)

        union = IntIntervals(union, is_sorted=True)
        if inplace:
            self.intervals = union.intervals
            return self

        return union

    def __or__(self, other):
        """Return the union of this with other."""
        return self.union(other)

    def intersection(self, other):
        """Return the intersection of this with other.

        Works in O(n) time where n is the number of intervals in both
        IntIntervals.

        """
        if not other:
            return IntIntervals([])
        intersection = []
        j = 0
        for interval in self.intervals:
            while j < len(other.intervals):
                intv_intersection = self._interval_intersect(interval,
                                                             other.intervals[j])
                if intv_intersection:
                    intersection.append(intv_intersection)
                    if other.intervals[j][1] <= interval[1]:
                        j += 1
                    else:
                        break
                else:
                    if other.intervals[j][1] < interval[0]:
                        j += 1
                    else:
                        break
        return IntIntervals(intersection, is_sorted=True)

    def __and__(self, other):
        """Return the intersection of this with other."""
        return self.intersection(other)

    def difference(self, other):
        """Return the set-theoretic difference of this with other.

        Works in O(n) time where n is the number of intervals in both
        IntIntervals.

        """
        if not other:
            return self.copy()
        j = 0
        difference = []
        for interval in self.intervals:
            while j < len(other.intervals):
                if self._check_intersect(interval, other.intervals[j]):
                    # There is an intersection, so we remove something.
                    diff = self._interval_difference(interval,
                                                     other.intervals[j])
                    if diff:
                        if len(diff) == 1:
                            if interval[0] < other.intervals[j][0]:
                                difference += diff
                                break
                            else:
                                j += 1
                                interval = diff[0]
                        else:
                            difference.append(diff[0])
                            interval = diff[1]
                            j += 1
                    else:
                        break
                else:
                    if interval[1] < other.intervals[j][0]:
                        difference.append(interval)
                        break
                    else:
                        j += 1
            if j >= len(other.intervals) and interval:
                difference.append(interval)
        return IntIntervals(difference, is_sorted=True)

    def __sub__(self, other):
        """Return the set-theoretic difference of this with other."""
        return self.difference(other)

    def symmetric_difference(self, other):
        """Return the symmetric difference of this with other.

        Works in O(n) time where n is the number of intervals in both
        IntIntervals.

        """
        return self.union(other).difference(self.intersection(other))

    def __xor__(self, other):
        """Return the symmetric difference of this with other."""
        return self.symmetric_difference(other)

    def copy(self):
        """Return a new IntInterval that is a copy of this one."""
        return IntIntervals(self.intervals[:], is_sorted=True)

    def smallest(self):
        """Return the smallest value in the intervals.

        Returns None if this is empty.

        """
        if self:
            return self.intervals[0][0]
        return None

    def largest(self):
        """Return the largest value in the intervals.

        Returns None if this is empty.

        """
        if self:
            return self.intervals[-1][1]
        return None

    def __hash__(self):
        """Return a hash for this."""
        if not self.intervals:
            return hash(None)
        cur_hash = hash(self.intervals[0])
        for interval in self.intervals[1:]:
            cur_hash ^= hash(interval)
        return cur_hash

    def __str__(self):
        """Return a string representation of the intervals."""
        string = ''
        for interval in self.intervals:
            if interval[0] == interval[1]:
                string += '{0},'.format(interval[0])
            else:
                string += '{0}-{1},'.format(interval[0], interval[1])
        return string[:-1]

    def __repr__(self):
        """Return a raw representation of the intervals."""
        return repr(self.intervals)
