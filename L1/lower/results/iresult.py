#!/usr/bin/python3
# encoding: utf-8

class IResult(object):
    pass

class IRecordable(object):
    @property
    def records(self):
        pass

    @property
    def records_count(self):
        pass

    def add_record(self, *args, **kwargs):
        pass

    def set_records(self, records):
        pass

    def keep_indices(self, indices, to_omit=None):
        records = self.records
        records_count = self.records_count
        to_omit = to_omit or ()
        if not indices:
            indices = range(0, records_count)
        records = [x for i, x in enumerate(records) if i not in to_omit and (
            i in indices or (i < 0 and (records_count+i) in indices))]
        self.set_records(records)

class IFileLinable(object):
    def as_file_line_list(self):
        pass
