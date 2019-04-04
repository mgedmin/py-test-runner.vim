if !exists("g:pyVimRunCommand")
  let g:pyVimRunCommand = ""
endif
if !exists("g:pyTestRunner")
  let g:pyTestRunner = ""
endif
if !exists("g:pyTestRunnerCommand")
  let g:pyTestRunnerCommand = ""
endif
if !exists("g:pyTestLastTest")
  let g:pyTestLastTest = ""
endif

function pytestrunner#use(runner, ...)
  let g:pyTestRunner = a:runner
  let g:pyTestRunnerCommand = join(a:000, " ")
endf

function pytestrunner#get_run_command()
  if g:pyVimRunCommand != ""
    return g:pyVimRunCommand
  elseif exists(":Make")
    return "Make"
  else
    return "make"
  endif
endf

function pytestrunner#get_test_command()
  pyx import py_test_runner, vim
  return pyxeval("py_test_runner.get_test_command(vim.current.buffer.name)")
endf

function pytestrunner#get_tag_under_cursor()
  if exists("*TagInStatusLine")
    " defined by https://github.com/mgedmin/pythonhelper.vim
    return TagInStatusLine()
  else
    return ""
  endif
endf

function pytestrunner#get_test_under_cursor()
  let tag = pytestrunner#get_tag_under_cursor()
  pyx import py_test_runner, vim
  return pyxeval("py_test_runner.get_test(vim.current.buffer.name, vim.eval('l:tag'))")
endf

function pytestrunner#get_clipboard_command()
  let tag = pytestrunner#get_tag_under_cursor()
  pyx import py_test_runner, vim
  return pyxeval("py_test_runner.get_clipboard_command(vim.current.buffer.name, vim.eval('l:tag'))")
endf

function pytestrunner#run(test)
  if a:test != ""
    silent! wall
    if hlexists("StatusLineRunning")
      hi! link StatusLine StatusLineRunning
    endif
    let g:pyTestLastTest = a:test
    let l:oldmakeprg = &makeprg
    let l:command = pytestrunner#get_test_command()
    echo l:command a:test
    try
      let &makeprg = l:command
      exec pytestrunner#get_run_command() a:test
    finally
      let &makeprg = l:oldmakeprg
    endtry
  endif
endf

function pytestrunner#run_test_under_cursor()
  call pytestrunner#run(pytestrunner#get_test_under_cursor())
endf

function pytestrunner#run_last_test_again()
  call pytestrunner#run(g:pyTestLastTest)
endf

function pytestrunner#copy_test_under_cursor()
  let l:cmd = pytestrunner#get_clipboard_command()
  if l:cmd != ""
    echo l:cmd
    let @* = l:cmd
  endif
endf
