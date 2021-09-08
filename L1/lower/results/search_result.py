#!/usr/bin/python3
# encoding: utf-8

from common.stringification import Stringification
from common import utils, logging
from L1.lower.results.iresult import IResult

class Record(object):
    def __init__(self, path=None, line=None, text=None, text_colored=None, caller=None, pre_ctx=None, post_ctx=None, is_decl=False):
        self.path = path or ''
        self.line = line and int(line) or ''
        self.text = text or ''
        self.text_colored = text_colored or ''
        if caller:
            c_line, c_text = caller
            self.caller = int(c_line), c_text
        else:
            self.caller = (0, '')
        self.pre_ctx = pre_ctx or []
        self.post_ctx = post_ctx or []
        self.is_decl = is_decl

    @classmethod
    def __default_of(cls, d):
        return cls().get(d)

    # TODO this should be part of the interface for IRes.Record
    def get(self, key, default=None):
        try:
            return vars(self)[key]
        except Exception as e:
            return default

    @classmethod
    def from_dict(cls, d):
        return Record(**d)

    def trim(self):
        self.text = self.text.strip()
        self.text_colored = self.text_colored.strip()

    def keep_only(self, elements, trim_on_sort=True):
        self.assert_has_elements(elements)
        new_dict = {}
        for k, v in self.__dict__.items():
            if k in elements:
                new_dict[k] = v
            else:
                new_dict[k] = self.__default_of(k)
        self.__dict__ = new_dict

    def jsonize(self):
        return utils.jsonize(self.__dict__)

    def humanize(self, i, **kwargs):
        return Stringification.stringify_record(i, self.__dict__, **kwargs)

    def raw_text(self, i, **kwargs):
        return self.humanize(i, colored=False, **kwargs)

    def stringify_by_args(self, **kwargs):
        return Stringification.stringify_by_args(self, **kwargs)

    def assert_has_elements(self, elements):
        assert self.has_elements(
            elements), f'One or more invalid element: {elements}'

    def has_elements(self, elements):
        class NotFound:
            pass
        for d in elements:
            if self.get(d, NotFound) == NotFound:
                return False
        return True


class SearchResult(IResult):
    def __init__(self, records=None):
        self._records = records or []
    @property
    def records(self):
        return self._records

    @property
    def paths(self):
        return [r.path for r in self._records]

    @property
    def texts(self):
        return [r.text for r in self._records]

    @property
    def lines(self):
        return [r.line for r in self._records]

    @property
    def texts_colored(self):
        return [r.text_colored for r in self._records]

    @property
    def records_count(self):
        return len(self._records)

    def add_record(self, *args, **kwargs):
        r = Record(*args, **kwargs)
        if (path := utils.should_ignore_record(r)):
            logging.verbose_print(f'Ignoring record with path: {path}')
            return
        self.records.append(r)

    @classmethod
    def from_dicts(cls, l):
        records = [Record.from_dict(d) for d in l]
        return SearchResult(records)

    def keep_indices(self, indices, to_omit=None):
        to_omit = to_omit or ()
        if not indices:
            indices = range(0, len(self._records))
        self._records = [x for i, x in enumerate(self._records) if i not in to_omit and (
            i in indices or (i < 0 and (len(self._records)+i) in indices))]

    def trim(self):
        for r in self._records:
            r.trim()

    def keep_only(self, elements, sort, unify, do_choice, trim_on_sort=True):
        assert (not unify) or len(
            elements) == 1, 'Cannot unify with more/less than a single element.'

        if not len(self._records):
            return

        self._records[0].assert_has_elements(elements)

        if sort:
            def sort_func(r):
                new = []
                for d in elements:
                    s = r.get(d, Record.__default_of(d))
                    if isinstance(s, str) and trim_on_sort:
                        s = s.strip()
                    new.append(s)
                return new
            self._records.sort(key=sort_func)
        elif do_choice:  # Ignore do_choice when sort is requested.
            for r in self._records:
                r.keep_only(elements)

        if unify:
            values = []
            d = elements[0]
            to_remove = []
            for i, r in enumerate(self._records):
                rval = r.get(d)
                if rval in values:
                    to_remove.append(i)
                else:
                    values.append(rval)
            self._records = [r for i, r in enumerate(
                self._records) if i not in to_remove]

    def filter_by_element(self, element, value_list):
        self._records = [
            r for r in self._records if r.get(element) in value_list]

    """ SHORTCUTS functions for stuff that use self/self._records as arg """

    def jsonize(self):
        return utils.jsonize(self._records)

    def humanize(self):
        return Stringification.stringify_output(self._records)

    def raw_text(self):
        return Stringification.raw_text(self._records)

    def picklize(self):
        return utils.picklize(self)

    def stringify_by_args(self, **kwargs):
        return Stringification.stringify_by_args(self, **kwargs)

    def is_empty(self):
        return not self.records

    def __str__(self):
        if self.is_empty():
            return f'<Empty SearchResult>'
        else:
            return f'<SearchResult with {self.records_count} records>'
