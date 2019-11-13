import os
from cudatext import *
from . import opt

fn_config = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_colored_indent.ini')
MARKTAG = 103 #uniq value for all ed.attr() plugins

def bool_to_str(v): return '1' if v else '0'
def str_to_bool(s): return s=='1'

_theme = app_proc(PROC_THEME_SYNTAX_DICT_GET, '')

def _theme_item(name):
    if name not in _theme:
        return 0x808080
    else:
        return _theme[name]['color_back']

def get_indent(s):
    for i in range(len(s)):
        if s[i] not in (' ', '\t'):
            return s[:i]
    return ''

class Command:
    active = True

    def __init__(self):

        opt.color_error = ini_read(fn_config, 'op', 'color_error', opt.DEF_ERROR)
        self.color_error = _theme_item(opt.color_error)

        opt.color_set = ini_read(fn_config, 'op', 'color_set', opt.DEF_SET)
        self.color_set = [_theme_item(i) for i in opt.color_set.split(',')]

        opt.lexers = ini_read(fn_config, 'op', 'lexers', opt.DEF_LEXERS)
        opt.max_lines = int(ini_read(fn_config, 'op', 'max_lines', '2000'))

        app_proc(PROC_SET_EVENTS, ';'.join([
            'cuda_colored_indent',
            'on_open,on_change_slow',
            opt.lexers
            ]))

    def toggle(self):

        self.active = not self.active
        msg_status('Colored Indent: '+('on' if self.active else 'off'))

        for h in ed_handles():
            e = Editor(h)
            if self.active:
                if self.lexer_ok(e):
                    self.work(e)
            else:
                e.attr(MARKERS_DELETE_BY_TAG, tag=MARKTAG)


    def on_start(self, ed_self):

        pass

    def get_color(self, n):

        return self.color_set[n%len(self.color_set)]

    def config(self):

        ini_write(fn_config, 'op', 'lexers', opt.lexers)
        ini_write(fn_config, 'op', 'color_error', opt.color_error)
        ini_write(fn_config, 'op', 'color_set', opt.color_set)
        ini_write(fn_config, 'op', 'max_lines', str(opt.max_lines))
        file_open(fn_config)

    def on_change_slow(self, ed_self):

        self.work(ed_self)

    def on_open(self, ed_self):

        self.work(ed_self)

    def lexer_ok(self, ed):

        lex = ed.get_prop(PROP_LEXER_FILE)
        return lex and (','+lex+',' in ','+opt.lexers+',')

    def work(self, ed):
        if not self.active:
            return

        if ed.get_line_count()>opt.max_lines:
            return

        tab_size = ed.get_prop(PROP_TAB_SIZE)
        tab_spaces = ed.get_prop(PROP_TAB_SPACES)

        ed.attr(MARKERS_DELETE_BY_TAG, tag=MARKTAG)

        lines = ed.get_text_all().splitlines()
        for (index, s) in enumerate(lines):
            indent = get_indent(s)
            if not indent:
                continue

            level = -1
            x = 0

            while indent:
                level += 1
                if indent[0]=='\t':
                    ed.attr(MARKERS_ADD,
                        x=x,
                        y=index,
                        len=1,
                        tag=MARKTAG,
                        color_font=0,
                        color_bg=self.get_color(level),
                        )
                    indent = indent[1:]
                    x += 1
                elif indent[:tab_size]==' '*tab_size:
                    ed.attr(MARKERS_ADD,
                        x=x,
                        y=index,
                        len=tab_size,
                        tag=MARKTAG,
                        color_font=0,
                        color_bg=self.get_color(level),
                        )
                    indent = indent[tab_size:]
                    x += tab_size
                else:
                    ed.attr(MARKERS_ADD,
                        x=x,
                        y=index,
                        len=len(indent),
                        tag=MARKTAG,
                        color_font=0,
                        color_bg=self.color_error,
                        )
                    break
