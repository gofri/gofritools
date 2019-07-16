#!/usr/bin/python3
# encoding: utf-8
from L1.iprogram import IProgram
import argparse
import itertools
from enum import Enum, auto


class Select(IProgram):
    UNSELECT_SPECIAL_CHAR = '^'

    def _run_prog(self, search_res, ranges):
        max_index = search_res.records_count - 1
        omit_list = []
        omit_only = True  # Use entire range as base range if there are only omit instructions

        for r_index, r in enumerate(ranges):
            to_omit = False
            if r[0] == self.UNSELECT_SPECIAL_CHAR:  # handle omitting the range
                r = r[1:]
                # remove marker -- let keep_indices ignore the range
                del ranges[r_index][0]
                to_omit = True
            else:
                omit_only = False

            for i, b in enumerate(r):  # handle above-max and negative indices
                if b == self.CONST.MAX_RANGE:
                    r[i] = max_index
                elif b > max_index:
                    raise IndexError(f'Invalid index: {b} > {max_index}')
                elif b < 0:
                    r[i] = search_res.records_count + b
            assert r[0] <= r[1], f'Invalid indices (left must be smaller than right: {r})'

            if to_omit:
                omit_list.append(r)

        # prepare omit list
        omit_list = [range(r[0], r[1] + 1) for r in omit_list]
        omit_list = self.__expand_ranges(omit_list)

        if omit_only:
            ranges = [range(0, max_index+1)]
        else:
            ranges = [range(r[0], r[1] + 1) for r in ranges]
        expanded = self.__expand_ranges(ranges)
        search_res.keep_indices(expanded, omit_list)
        return search_res

    def __expand_ranges(self, ranges):
        return set(itertools.chain.from_iterable(ranges))

    class CONST(Enum):
        MAX_RANGE = auto()

    @classmethod
    def RangeType(cls, r):
        r = r.strip()
        omit_mark = False

        if not r:
            raise argparse.ArgumentError("Empty range value")

        # Options:
        # N     A single line
        # N+    A specific line and all lines after it
        # N-    A specific line and all lines before it
        # N:N   An inclusive range of lines
        # -N    Reversed index, like python. When the left (or single) arg is negative, use +-N instead (see comment below)
        # ^P    (where P is any expression) Unselect these lines. No ordering: all unselected lines will not show in result, even if these lines are in a later range.

        # Enable the user to insert e.g. '+-1' instead of '-1', because -1 is confused as an optional arg.
        if r.startswith(cls.UNSELECT_SPECIAL_CHAR):
            r = r[1:]
            omit_mark = True

        if r.startswith('+-'):
            r = r[1:]

        if r.endswith('+'):
            r, _ = r[:-1], r[-1]
            r = [int(r), cls.CONST.MAX_RANGE]
        elif r.endswith('-'):
            r, _ = r[:-1], r[-1]
            r = [0, int(r)]
        else:
            if ':' in r:
                r = [int(x) for x in r.split(':')]
            else:
                r = [int(r), int(r)]

            if (r[0] >= 0 and r[1] >= 0) or (r[0] < 0 and r[1] < 0):
                testres = r[0] <= r[1]
                assert r[0] <= r[1], 'Lefthand bound must be smaller than Righthand bound'
            else:
                pass  # Cannot determine without range size -- let the user validate it

        assert len(r) == 2, 'Invalid range'

        if omit_mark:
            r = [cls.UNSELECT_SPECIAL_CHAR] + r

        return r
