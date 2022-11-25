" File: py-test-runner.vim
" Author: Marius Gedminas <marius@gedmin.as>
" Version: 1.4.0
" Last Modified: 2022-11-25
"
" Overview
" --------
" Vim script to run a unit test you're currently editing.
"
" Probably very specific to the way I work.
"
" Installation
" ------------
" Make sure you have taghelper.vim or pythonhelper.vim installed.
" Then copy the three files (plugin/py-test-runner.vim,
" autoload/pytestrunner.vim and pythonx/py_test_runner.py) into the
" corresponding directories under $HOME/.vim.
" Or, better, use a plugin manager like vim-plug:
"
"     Plug 'mgedmin/taghelper.vim'
"     Plug 'mgedmin/py-test-runner.vim'
"
" This plugin most likely requires vim 7.0 or maybe even 8.0.  It also needs
" Vim with Python 3 support.
"
" Usage
" -----
" :call pytestrunner#use("pytest") -- use pytest (default)
" :call pytestrunner#use("nose")   -- use nosetests
" :call pytestrunner#use("zope")   -- use zope.testrunner
" :call pytestrunner#use("django") -- use bin/django test
" :call pytestrunner#use("pytest", "venv/bin/pytest") -- use pytest from venv
" :call pytestrunner#use("pytest", "pytest -vv")      -- pass extra arguments
"
" :RunTestUnderCursor -- launches the test runner (configured via
" g:pyTestRunner) with :make
"
" :RunTest [<class>.]<test> -- launches the test runner for a given test
" in the current file
"
" :RunLastTestAgain -- runs the last test again (useful when you've moved the
" cursor away while editing)
"
" :CopyTestUnderCursor -- copies the command line to run the test into the
" X11 selection
"

" Backwards compatibility
function! UseZopeTestRunner(...)
  " Assumes you have bin/test, generates command lines of the form
  "   bin/test -s <package> -m <module> -t '{method} [(].*{class}[)]'
  call pytestrunner#use("zope", join(a:000, " "))
endfunction

function! UseDjangoTestRunner(...)
  " Assumes you have django-nose, generates command lines of the form
  "   bin/django test <filename>:{class}.{method}
  call pytestrunner#use("django", join(a:000, " "))
endfunction

function! UsePyTestTestRunner(...)
  " Assumes you have py.test, generates command lines of the form
  "   pytest <filename>::{class}::{method}
  call pytestrunner#use("pytest", join(a:000, " "))
endfunction

function! UseNoseTestRunner(...)
  " Assumes you have nose, generates command lines of the form
  "   nosetests <filename>:{class}.{method}
  call pytestrunner#use("nose", join(a:000, " "))
endfunction

command! -bar RunTestUnderCursor  call pytestrunner#run_test_under_cursor()
command! -bar -nargs=1 RunTest    call pytestrunner#run_test(<q-args>)
command! -bar RunLastTestAgain    call pytestrunner#run_last_test_again()
command! -bar CopyTestUnderCursor call pytestrunner#copy_test_under_cursor()
