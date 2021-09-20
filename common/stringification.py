#!/usr/bin/python3
# encoding: utf-8

from common import ui_tools, utils
from builtins import classmethod



# TODO move (at least most of it) to search_result

class Stringification(object):
    @classmethod
    def stringify_output(cls, output, colored=True, **kwargs):
        ''' for multiple records '''
        return ui_tools.get_as_incrementing_list(output, cls.stringify_record, is_colored=colored, **kwargs)

    @classmethod
    def stringify_record(cls, i, r, colored=True, **kwargs):
        path = cls.colored_or_nothing(r, 'path', colored)
        line = str(cls.colored_or_nothing(r, 'line', colored))
        text = r.get('text', '')
        colored_text = r.get('text_colored', '')
        caller_line, caller_text = r.get('caller', ('', ''))
        pre_ctx, post_ctx = r.get('pre_ctx', ''), r.get('post_ctx', '')
        is_decl = r.get('is_decl', False)

        if colored and colored_text:
            text = colored_text

        text = text and text.strip()

        separator = ui_tools.colored(':', key='separator') if colored else ':'
        only_existing = [x for x in [path, line, text] if x]
        text = separator.join(only_existing)
        ''' TODO properly present context
        if pre_ctx:
            text = '\n'.join(pre_ctx + [text])
        if post_ctx:
            text = '\n'.join([text] + post_ctx)
        '''

        context = ''
        break_before = ''
        if caller_text:
            separator = ui_tools.colored(
                ':', key='separator') if colored else ':'
            if is_decl:
                htext = '== DECLARATION'
                c_header = ui_tools.colored(htext, key='declaration') if colored else htext
            else:
                htext = '== CALLER'
                c_header = ui_tools.colored(htext, key='caller') if colored else htext

            caller_line = ui_tools.colored(
                caller_line, key='line') if colored else str(caller_line)
            joined = separator.join((c_header, caller_line, caller_text))
            if i > 0:
                break_before = '\n'
            context = joined + '\n' if joined else ''
        elif is_decl:
            separator = ui_tools.colored(
                ':', key='separator') if colored else ':'
            htext = '== DECLARATION' if text.strip().endswith(';') else '== DEFINITION' # TODO should be a separate field (is_decl/is_definition)
            c_header = ui_tools.colored(
                htext, key='declaration') if colored else htext
            joined = separator.join((c_header, ''))
            context = joined + '\n'


        max_size = kwargs.get('max_line_size')
        if len(text) > max_size:
            warning = ui_tools.colored(f'<Warning [from gofritools]: the text above is truncated from {len(text)} to {max_size} chars>', color='red')
            text = text[:max_size] + '\n' + warning
        return text, context, break_before

    @classmethod
    def colored_or_nothing(cls, r, key, colored=True):
        text = r.get(key, '')

        if not colored or not text:
            return text

        return ui_tools.colored(text, key=key)

    @classmethod
    def raw_text(cls, data, prev_context=None):
        ''' for multiple records '''
        res = ''
        prev_context = prev_context or ''
        for i, d in enumerate(data):
            text, new_context, break_before = d.raw_text(
                i, prev_context=prev_context)
            if prev_context == new_context:
                new_context = ''
            res += f'{break_before}{new_context}\t{text}\n'
            prev_context = new_context or prev_context  # ignore double
        return res

    @classmethod
    def stringify_by_args(cls, data, output_type, **kwargs):
        choice = utils.OutputTypes.make_choice(
            output_type, r=data.raw_text, h=data.humanize, j=data.jsonize)
        return choice(**kwargs)
