#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L1.gql import GQL
import readline
import shlex

class GqlCompletion(object):
    def __init__(self):
        self._options = self.__list_default_options()

    @property
    def options(self):
        return list(self._options)

    def __list_default_options(self):
        return self.__list_python_keywords() + \
                self.__list_record_fields()

    PY_KEYWORDS_WHITELIST = ['False', 'None', 'True', 'and', 'break', 'continue', 'def', 'elif', 'else', 'except', 'finally', 'for', 'if', 'in', 'is', 'lambda', 'not', 'or', 'pass', 'return', 'try', 'while', 'with', 'yield']
    def __list_python_keywords(self):
        # import keyword; return keyword.kwlist
        return self.PY_KEYWORDS_WHITELIST

    def __list_record_fields(self):
        # TODO this should be replaced with a gql-based functionality.
        # In addition, stuff like path.<TAB> should yield gql-based funcs (StrField, PathField, etc.)
        from L1.lower.results.search_result import Record
        return list(vars(Record()).keys())

    def register(self):
        readline.set_completer_delims(' ')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.completer)
        readline.set_completion_display_matches_hook(self.display)

    def completer(self, text, state):
        try:
            # print(f'text: "{text}", state: "{state}", buf: {readline.get_line_buffer()}')
            org_text = text
            if text != '':
                text = readline.get_line_buffer()
            options = self.options
            if text:
                # TODO replace shlex with iterating tokenize
                # tokenize.tokenize(io.BytesIO(text.encode('utf-8')).readline
                text = shlex.split(text)[-1]
                pre_text = org_text[:org_text.rfind(text)]
                options = [pre_text + o for o in options if o.startswith(text)]
                 
            options.append(None)
            return options[state]
        except Exception as e:
            print(e)

    def display(self, substitution, matches, longest_match_length):
        try:
            # print(f'\nsub: "{substitution}",\nm: "{matches}",\nlo: "{longest_match_length}"')
            if substitution:
                start_off = substitution.rfind(shlex.split(substitution)[-1])
                matches = [m[start_off:] for m in matches]
            print('\n' + '\t'.join(matches) + '\n' + substitution, end='')
        except Exception as e:
            print(f'failed: {e}')

    def input(self):
        return input()        

class VirtGql(IVirt):
    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, _underlying_prog_t=GQL, stackable=True, dirtying=False)
        self.completer = GqlCompletion()
        self.completer.register()

    def _run_virt(self, **kwargs):
        # XXX: need to change for search res
        query = kwargs.get('query', '')
        if not query or not query.strip():
            query = self.prompt_query()
        kwargs['query'] = query
        kwargs['data'] = self.prev_output
        self._underlying_prog.run(**kwargs)
        return self._underlying_prog.output
    
    def prompt_query(self):
        return self.completer.input()
