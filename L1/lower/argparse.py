import argparse

class FileLine(object):
    SEPARATOR = ':'

    def __init__(self, file_, line=''):
        file_ = file_.strip()
        line = str(line).strip()
        if not file_:
            raise argparse.ArgumentError((file_, line), "invalid missing file")
        if line and int(line) < 0:
            raise argparse.ArgumentError(line, "Invalid line")

        self.file = file_
        self.line = line

    @staticmethod
    def order_key(fl):
        try:
            line = int(fl.line)
        except Exception:
            line = -1 # no-line implies whole-file, so set it first
        return (fl.file, line)

    @classmethod
    def from_str(cls, fileline):
        return cls.from_tuple(fileline.split(cls.SEPARATOR))

    @classmethod
    def from_tuple(cls, tup):
        return cls(*tup)

    @classmethod
    def as_safe_list(cls, fl_list, sorted_=True, unique=True, reverse=True):
        '''
            Safe list of file-line.
                Sorted: a consistent order.
                Unique: avoid duplicate actions.
                Reverse: when deleting lines, avoid the need to take deleted lines into account.
        '''
        if unique:
            fl_list = {cls.order_key(fl):fl for fl in fl_list}.values()
        if sorted_:
            fl_list = sorted(fl_list, key=cls.order_key, reverse=reverse)

        return fl_list

    @classmethod
    def L2_combine_pairs(cls, kwargs, records):
        KEY = 'pairs'
        pairs = kwargs[KEY] or []
        pairs += [cls(r.path, r.line) for r in records]
        kwargs[KEY] = pairs
        return kwargs

    def __str__(self):
        return f'{self.file}:{self.line}'
    
    def __repr__(self):
        return str(self)

def common_pattern_parser():
    ''' Common flags for cmds with a pattern '''
    common_pattern = argparse.ArgumentParser(add_help=False)
    common_pattern.add_argument(
        'pattern', help='The pattern to test', default=['.*'], nargs='*')
    common_pattern.add_argument('-i', '--case-insensitive', dest='case_sensitive',
                                help='Case sevsitive search (insensitive by default)', action='store_false', default=True)
    common_pattern.add_argument('-@', '--wildness', help='Use incrementally wilder search (1=surround by wildcards. 2=convention variations)',
                                action='count', default=0)
    common_pattern.add_argument(
        '-f', '--files', help='Limit the operation to specific files / directories', type=str, nargs='+', default=[])

    return common_pattern

def common_file_line_parser():
    common_file_line = argparse.ArgumentParser(add_help=False)
    common_file_line.add_argument(
        'pairs', help='One or more [file]s or [file,line] pairs', type=FileLine.from_str, nargs="*")

    return common_file_line
