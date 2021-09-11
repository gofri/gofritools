import argparse
from common import ui_tools
from common import utils

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

    def colored(self):
        file = ui_tools.colored(self.file, key='path')
        if self.line is None:
            return f'{self.file}'
        sep = ui_tools.colored(':', key='separator')
        line = ui_tools.colored(self.line, key='line')
        return f'{file}{sep}{line}'

    def __str__(self):
        if self.line is None:
            return f'{self.file}'
        else:            
            return f'{self.file}:{self.line}'
    
    def __repr__(self):
        return str(self)

    class LoopStop: pass
    class LoopEnter: pass
    @classmethod
    def _loop_prompt(cls):
        while True:
            print(f'Press enter to continue, s/stop to stop')
            choice = input().strip()
            if choice in ('s', 'stop'):
                return cls.LoopStop
            elif choice == '':
                return cls.LoopEnter
            else:
                print('Invalid choice.')

    @classmethod
    def interactive_file_series(cls, pairs, hook, do_reverse=False):
        files = [p.file for p in pairs]
        with utils.MultipleFiles(files):
            pairs = FileLine.as_safe_list(pairs, sorted_=do_reverse)
            if len(pairs) == 1:
                hook(pairs[0])
            else:
                for p in pairs:
                    print(f'Showing {ui_tools.highlight(p)}')
                    choice = cls._loop_prompt()
                    if choice == cls.LoopStop:
                        print('stopped.')
                        return
                    elif choice == cls.LoopEnter:
                        hook(p)
                print('done.')
