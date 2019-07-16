#!/usr/bin/python3
# encoding: utf-8

from common import utils, logging
from common.utils import in_kwargs
from L1.iprogram import IProgram
from common.res import SearchRes
from enum import Enum
import itertools
from L0.ishell import IShell

GREP_RC_NO_RES = 1

class Res(Enum):
    SUCCESS = 0
    NO_RESULT = 1
    ERR = 2

class Grep(IProgram):
    RESULT_SEPARATOR = ':'
    CALLER_SEPARATOR = '='
    
    def _run_prog(self, **kwargs):
        no_color = self.__grep_base_no_color(**kwargs)
        colored = self.__grep_base_colored(**kwargs)

        parsed = self.__parse_output(
            no_color['stdout'], colored['stdout'], **kwargs)
        return parsed

    def params(self):
        return utils.get_func_args(self.__grep_base_no_color)

    def __grep_base_colored(self, **kwargs):
        extra_flags = ['--color=always']
        if 'extra_flags' in kwargs:
            extra_flags = kwargs['extra_flags'] + extra_flags
            del kwargs['extra_flags']

        return self.__grep_base_no_color(extra_flags=extra_flags, **kwargs)

    def __grep_base_no_color(self, pattern, git, text, files, wildness, context, extra_flags, case_sensitive, whole_word, exclude_files, invert, untracked):
        IGNORE_BIN_FILES = '-I'
        SHOW_FILE_LINE = '-n'
        REGEX_SEARCH = '-E'
        SUPPRESS_PERM_ERRORS = ''  # '-s' # see below: ignoring stderr instead
        SEPARATE_FILES = ['--heading', '--break'] # File name as a single line after an empty line

        pattern = [utils.get_wild_version(p, wildness) for p in pattern]
        whole_word = '-w' if whole_word else ''
        invert = '-v' if invert else ''
        case_flag = '' if case_sensitive else '-i'
        context = '--function-context' if context else ''
        extra_flags = extra_flags or ''
        untracked = '--untracked' if untracked else ''

        if exclude_files:
            # https://ask.xiaolee.net/questions/1085445
            exclude_files = [f':(exclude){x}' for x in exclude_files]
            # exclude in git is practically just a native hack of files specification
            files += exclude_files

        pattern = list(itertools.chain(*[('-e', p) for p in pattern]))

        util = self.__get_util(git)

        cmd = util.split() + \
            [SUPPRESS_PERM_ERRORS, REGEX_SEARCH, IGNORE_BIN_FILES, SHOW_FILE_LINE, *SEPARATE_FILES] + \
            [case_flag, whole_word, context, invert, untracked, *extra_flags] + \
            pattern + \
            ['--'] + \
            (files or [])      

        # Use stdout_enough because grep return EIOERROR even if perm messages are suppressed
        try:
            res = self.ishell.run_cmd(cmd, stdin=text, stdout_enough=True)
        except IShell.CmdFailureException as e:
            if e.res['rc'] == Res.NO_RESULT.value:
                return IShell.empty_res()
            else:
                raise

        return res

    def __get_util(self, git):
        if git: 
            # Allow fallback
            return 'git -c grep.fallbackToNoIndex=true grep'
        else:
            # Force no-index (e.g. when running from a repo but searching outside the repo)
            return 'git grep --no-index'

    def __parse_output(self, output, output_colored, *args, **kwargs):
        return Parsing().parse_with_func_ctx(output, output_colored)

class InlineSeparator(Enum):
    CALLER = '='
    DECLARATION_OR_USAGE = ':'
    CONTEXT = '-'

class LineSeparator(Enum):
    FILE = ''
    RESULT = '--'

class NewFile(Exception):
    def __init__(self, name):
        Exception.__init__(self)
        self.name = name

class LineSeparatorExc(Exception):
    def __init__(self, sep):
        Exception.__init__(self)
        self.sep = sep

class ParsedLine(object):
    def __init__(self, path, line, text):
        self.path = path
        self.line = line
        self.text = text

class Parsing(object):

    def __init__(self):
        self.cur_file = None
        self.post_match = False
        self.in_res = False
        self.pre_ctx = []
        self.caller = []

    def __split_line(self, line):
        indices = {s:index for s in InlineSeparator if (index:=line.find(s.value)) != -1}
        assert indices, 'must be at least one of them'
        sep = min(indices, key=(lambda k:indices[k]))
        
        # sep, line, text
        return [sep] + line.split(sep.value, 1)

    def __get_colored_text(self, line):
        return line.split(InlineSeparator.DECLARATION_OR_USAGE.value, 1)[1]

    def __parse_line(self, line):
        ''' line -> Either:
                * LineSeparator(new file / new result)
                * InlineSeparator, path, line, text
        '''
        line = line.strip()
        if self.cur_file:    
            try:
                # Look for file/result separator -- raise exception if found, except ValueError otherwise.
                line_sep = LineSeparator(line)
                raise LineSeparatorExc(line_sep)
            except ValueError:
                pass
        else:
            raise NewFile(line)
        
        return self.__split_line(line)

    def parse_with_func_ctx(self, output, output_colored):
        res = output.splitlines()
        res_colored = output_colored.splitlines()
        parsed = SearchRes()
        self.cur_file = None

        for i, line in enumerate(res):

            # Parse line / get line-separator
            try:
                sep, line_no, line_text = self.__parse_line(line)
            except LineSeparatorExc as sep_exc:
                # logging.verbose_print(f'grep parsing line: {line}', min_verbosity=logging.VERBOSE_3)

                sep = sep_exc.sep
                self.in_res = self.post_match = False
                self.pre_ctx = []
                self.caller = None
                if sep == LineSeparator.FILE:
                    self.cur_file = None
                continue
            except NewFile as newfile:
                self.cur_file = newfile.name
                continue
            
            if sep == InlineSeparator.DECLARATION_OR_USAGE:
                is_decl = not self.in_res
                text_colored = self.__get_colored_text(res_colored[i])
                if any([self.cur_file.endswith('.c'), self.cur_file.endswith('.h')]): # heuristic: only for c
                    if self.caller and self.caller[1].strip().startswith('struct'): # herusitic: if within struct, this is a defintion
                        is_decl = True
                    parsed.add_record(path=self.cur_file, line=line_no, text=line_text, text_colored=text_colored,
                                        caller=self.caller, pre_ctx=list(self.pre_ctx), is_decl=is_decl)
                else:
                    parsed.add_record(path=self.cur_file, line=line_no, text=line_text, text_colored=text_colored)

            elif sep == InlineSeparator.CONTEXT:
                if self.post_match:
                    parsed.records[-1].post_ctx.append(line_text)
                else:
                    self.pre_ctx.append(line_text)
            elif sep == InlineSeparator.CALLER:
                self.caller = (line_no, line_text.strip()) 
            else:
                raise ValueError(f'Unexpected separator ({sep})')

            self.in_res = True

        return parsed
