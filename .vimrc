" Specify a directory for plugins
" - For Neovim: stdpath('data') . '/plugged'
" - Avoid using standard Vim directory names like 'plugin'
" call plug#begin('~/.vim/plugged')

" Plug 'wellle/context.vim'

" Initialize plugin system
" call plug#end()

set number
" respect bashrc
" interactive
set shellcmdflag=-ic


" Enable plugins under e.g. ~/.vim/plugins/c
" See 	https://www.vim.org/scripts/script.php?script_id=2368
" :filetype plugin on

set tabstop=4       " The width of a TAB is set to 4.
                    " Still it is a \t. It is just that
                    " Vim will interpret it to be having
                    " a width of 4.

set shiftwidth=4    " Indents will have a width of 4

set softtabstop=4   " Sets the number of columns for a TAB

set expandtab       " Expand TABs to spaces
