Overview
--------

Vim script to run the tests for the current file/class/function.

Supports various Python test runners including

- pytest
- nose
- zope.testrunner
- django test

Demo:

.. image:: screencast.gif
   :alt: asciicast
   :width: 590
   :height: 396
   :align: center
   :target: https://asciinema.org/a/238972


.. contents::


Installation
------------

I recommend vim-plug_.

You'll also need pythonhelper.vim_, and I recommend asyncrun.vim_ too.

Needs Vim built with Python support.


Usage
-----

The plugin defines the following commands:


**:RunTestUnderCursor**

    Runs a single test function/method/class/module, depending on where your
    cursor is.  Can run the test asynchronously if you have asyncrun.vim_
    installed and have defined the ``:Make`` command `as documented in the wiki
    <https://github.com/skywind3000/asyncrun.vim/wiki/Replace-old-make-command-with-AsyncRun>`__.


**:RunLastTestAgain**

    Repeats the last test run.


**:CopyTestUnderCursor**

    Copies the command to run a single test function/method/class/module into
    the system clipboard, so you can paste it into a terminal window and not
    block your Vim instance.


Keyboard shortcuts
------------------

If you want some, copy and paste this into your .vimrc::

    map <C-F9> :RunTestUnderCursor<CR>
    map <C-S-F9> :RunLastTestAgain<CR>


Status line
-----------

If you're running the tests asynchronously it can be helpful to indicate the
test status (running/pass/fail) by changing the status line color.

You can define the higlight groups like ::

    hi StatusLineNeutral
                \ term=bold,reverse cterm=bold,reverse gui=bold,reverse
    hi StatusLineRunning ctermfg=53 guifg=#5f005f
                \ term=bold,reverse cterm=bold,reverse gui=bold,reverse
    hi StatusLineSuccess ctermfg=22 guifg=#005f00
                \ term=bold,reverse cterm=bold,reverse gui=bold,reverse
    hi StatusLineFailure ctermfg=52 guifg=#5f0000
                \ term=bold,reverse cterm=bold,reverse gui=bold,reverse
    hi! link StatusLine StatusLineNeutral

and then ``:RunTestUnderCursor`` will detect this and link *StatusLine* to
*StatusLineRunning* when the test process starts.  It's up to you to define
an asyncrun exit callback to link it to success/failure as appropriate::

    fun! OnAsyncRunExit()
      if g:asyncrun_status == 'success'
        hi! link StatusLine StatusLineSuccess
      elseif g:asyncrun_status == 'failure'
        hi! link StatusLine StatusLineFailure
      endif
      redrawstatus!
    endf
    let g:asyncrun_exit = "call OnAsyncRunExit()"

I'm considering removing the half-finished integration and suggesting you do
the initial linking via ::

    augroup AsyncRun
      au!
      au User AsyncRunStart hi! link StatusLine StatusLineRunning | redrawstatus!
    augroup END


Configuration file
------------------

This plugin reads **~/.vim/py-test-runner.cfg** if it exists.  It should be an INI
file like this::

    [default]
    runner = pytest

    [runner:mytestrunner]
    command = mytestrunner
    filter_for_file = {filename}
    filter_for_function = {filename}::{function}
    filter_for_class = {filename}::{class}
    filter_for_method = {filename}::{class}::{method}
    filter_for_doctest = -k {function}

    [path:~/src/myproject]
    runner = mytestrunner
    command = venv/bin/mytestrunner


[default] section
~~~~~~~~~~~~~~~~~

The ``[default]`` section has the following settings:


**runner**

    Specifies the default test runner.  If omitted, the default is ``pytest``.
    You can use any of the predefined test runners (``pytest``, ``nose``,
    ``zope``, and ``django``), or any custom test runner if you have a
    corresponding ``[runner:foo]`` section.

    This setting can be overridden by ``[path:...]`` sections and manually,
    if you ``:call pytestrunner#use(runner)`` or set ``g:pyTestRunner``.


**ignore_functions_and_methods**

    Specifies a whitespace-separated list of function/method names that
    should not be considered to be tests.

    For example, this is the default ignore list::

        [default]
        ignore_functions_and_methods =
            __init__
            setUp
            tearDown
            test_suite

    When the cursor is inside a function/method with one of these names,
    it will be ignored (and the scope of the test will be the entire
    module/class).

    This setting can be overridden by ``[runner:...]`` sections, and by
    ``[path:...]`` sections.


[runner:...] sections
~~~~~~~~~~~~~~~~~~~~~

The ``[runner:NAME]`` sections define/override test runners and have the
following settings:


**command**

    Specifies the main test runner command.  This can contain arguments.
    No shell escaping is done, so be careful!

    Examples::

        [runner:pytest]
        command = pytest -ra

        [runner:tox]
        command = tox -e py27,py37 --

    This setting can be overridden by ``[path:...]`` sections and manually, by
    calling ``pytestrunner#use(runner, command)`` or by setting
    ``g:pyTestRunnerCommand``.

    The full command is constructed from ``command`` and the multiple
    ``filter_for_...`` settings in the following order:

    #. command
    #. filter_for_file, if not blank
    #. filter_for_directory, if not blank
    #. filter_for_package, if not blank
    #. filter_for_module, if not blank
    #. one of filter_for_function, filter_for_doctest, filter_for_class,
       filter_for_method, whichever is applicable

    As a special case, if filter_for_function (or filter_for_doctest, or
    filter_for_class, or filter_for_method, whichever was picked) mentions the
    ``{filename}`` placeholder, filter_for_file, filter_for_directory,
    filter_for_package and filter_for_module will be skipped.


**filter_for_file**

    Specifies how to tell the test runner which test file is interesting.

    Example::

        [runner:pytest]
        filter_for_file = {filename}

    Whether the ``{filename}`` placeholder is replaced with a relative or
    absolute filename depends on the ``absolute_filenames`` setting.

    You will want to specify either ``filter_for_file`` or
    ``filter_for_module``, but not both.  (I don't know what will happen
    if you specify both.)

    This setting can be overridden by ``[path:...]`` sections.


**filter_for_directory**

    Specifies how to tell the test runner which test directory is interesting.

    Example::

        [runner:...]
        filter_for_directory = {directory}

    Whether the ``{directory}`` placeholder is replaced with a relative or
    absolute filename depends on the ``absolute_filenames`` setting.

    You will want to specify either ``filter_for_directory`` or
    ``filter_for_filename``, but not both.  (I don't know what will happen
    if you specify both.)

    You will want to specify either ``filter_for_directory`` or
    ``filter_for_package``, but not both.  (I don't know what will happen
    if you specify both.)

    This setting can be overridden by ``[path:...]`` sections.


**filter_for_package**

    Specifies how to tell the test runner which test package is interesting.

    Example::

        [runner:zope]
        filter_for_package = -s {package}

    The logic that computes Python package names from directory names
    relies on the presence/absence of ``__init__.py`` files and breaks if
    you use PEP-420 namespace packages.

    You will want to specify either ``filter_for_package`` or
    ``filter_for_filename``, but not both.  (I don't know what will happen
    if you specify both.)

    You will want to specify either ``filter_for_package`` or
    ``filter_for_directory``, but not both.  (I don't know what will happen
    if you specify both.)

    This setting can be overridden by ``[path:...]`` sections.


**filter_for_module**

    Specifies how to tell the test runner which test module is interesting.

    Example::

        [runner:zope]
        filter_for_module = -m {module}

    The module name is just the filename without the ``.py`` extension.

    You will want to specify either ``filter_for_module`` or
    ``filter_for_filename``, but not both.  (I don't know what will happen
    if you specify both.)

    This setting can be overridden by ``[path:...]`` sections.


**filter_for_function**

    Specifies how to tell the test runner which test function is interesting.

    Filtering by test function requires pythonhelper.vim_ to be installed.

    Examples::

        [runner:zope]
        filter_for_function = -t {function}

        [runner:pytest]
        filter_for_function = {filename}::{function}

    This setting can be overridden by ``[path:...]`` sections.


**filter_for_doctest**

    Specifies how to tell the test runner which doctest function is
    interesting.

    Filtering by test function requires pythonhelper.vim_ to be installed.

    Regular functions from doctest functions are distinguished by name
    (functions starting with ``test`` are assumed to be regular functions).

    Examples::

        [runner:zope]
        filter_for_doctest = -t {function}

        [runner:pytest]
        filter_for_doctest = -k {function}

    If this setting is not specified, ``filter_for_function`` is used
    instead for doctest functions as well.

    This setting can be overridden by ``[path:...]`` sections.


**filter_for_class**

    Specifies how to tell the test runner which test class is interesting.

    Filtering by test class requires pythonhelper.vim_ to be installed.

    Examples::

        [runner:zope]
        filter_for_class = -t {class}

        [runner:pytest]
        filter_for_class = {filename}::{class}

    If this setting is not specified, ``filter_for_function`` is used
    instead.

    This setting can be overridden by ``[path:...]`` sections.


**filter_for_method**

    Specifies how to tell the test runner which test method is interesting.

    Filtering by test method requires pythonhelper.vim_ to be installed.

    Examples::

        [runner:zope]
        filter_for_method = -t '{method} \(.*\.{class}\)'

        [runner:pytest]
        filter_for_class = {filename}::{class}::{method}

        [runner:nose]
        filter_for_class = {filename}::{class}.{method}

    If this setting is not specified, ``filter_for_function`` is used
    instead and gets the method name (discarding the class name).

    This setting can be overridden by ``[path:...]`` sections.


**absolute_filenames**

    Set to a true value (``true``, ``yes``, ``1``) if you want ``{filename}``
    and ``{directory}`` placeholders to be absolute.

    This is helpful when the test runner script changes its working directory
    before it starts looking for files.

    Set to a false value (``false``, ``no``, ``0``) if you want ``{filename}``
    and ``{directory}`` placeholders to be exactly as they appear in Vim
    (so they could be absolute or relative, depending on how you opened
    the file).

    Defauls to false.  Can be overridden by ``[path:...]`` sections.


**clipboard_extras**

    Extra command-line flags to be added when using :CopyTestUnderCursor.

    Use this to add colors or progress bars that would otherwise confuse Vim's
    :make.

    These flags are added to the beginning of the command line.

    Example::

        [runner:zope]
        clipboard_extras = -pvc

    This setting can be overridden by ``[path:...]`` sections.


**clipboard_extras_suffix**

    Extra command-line flags to be added when using :CopyTestUnderCursor.

    Use this to add colors or progress bars that would otherwise confuse Vim's
    :make.

    These flags are added to the end of the command line.

    No shell escaping is done so you can in fact do something like ::

        [runner:zope]
        clipboard_extras = 2>&1 | less -R

    to pipe the test runner's output to a pager.

    This setting can be overridden by ``[path:...]`` sections.


[path:...] sections
~~~~~~~~~~~~~~~~~~~

The ``[path:PATH]`` sections define overrides for your projects
identified by path names and have the following settings:

**runner**

    Overrides the ``runner`` from the ``[defaults]`` section.

    Example::

        [path:~/src/vim-plugins/py-test-checker.vim]
        command = coverage run -m pytest

    Can be overridden by setting ``g:pyTestRunner`` or calling
    ``pytestrunner#use(runner)``.

**command**

    Overrides the ``command`` from the ``[runner:...]`` section.

    Example::

        [path:~/src/vim-plugins/py-test-checker.vim]
        command = coverage run -m pytest

    Can be overridden by setting ``g:pyTestRunnerCommand`` or calling
    ``pytestrunner#use(runner, command)``.


**filter_for_file**,
**filter_for_directory**,
**filter_for_package**,
**filter_for_module**,
**filter_for_function**,
**filter_for_doctest**,
**filter_for_class**,
**filter_for_method**

    Override the corresponding setting from the ``[runner:...]`` section.

    You're not expected to ever need this.

**absolute_filenames**,
**clipboard_extras**,
**clipboard_extras_suffix**

    Override the corresponding setting from the ``[runner:...]`` section.

    These look like settings it can make sense to override on a
    per-project basis.  Maybe.


Global variables
----------------

The following global variables are used:

**g:pyVimRunCommand** (default: "")

    Vim command to run an external process (after setting ``&makeprg``).
    If blank, the plugin will use ``:Make`` if such a user-defined
    command exists, otherwise it will use ``:make``.

    asyncrun.vim_ recommends defining ::

      command! -bang -nargs=* -complete=file Make AsyncRun -program=make @ <args>

    so you can run commands in the background

**g:pyTestRunner** (default: "")

    Test runner to use.  If not blank, overrides the ``runner`` setting in the
    configuration file.

    The ``:call pytestrunner#use(...)`` convenience command writes to
    this variable.

**g:pyTestRunnerCommand** (default: "")

    Test runner command to use.  If not blank, overrides the ``command``
    setting in the configuration file.

    The ``:call pytestrunner#use(...)`` convenience command writes to
    this variable.

**g:pyTestLastTest** (default: "")

    This is not a configuration setting, but instead the filter describing
    the last test executed via :RunTestUnderCursor.  It is used by
    :RunLastTestAgain.



Backwards compatibility
-----------------------

There are several functions that streamline the setup for the most common test
runners, left for backwards compatibility:


**:call UsePyTestTestRunner("pytest -ra")**

    Use pytest, which uses commands like ::

        pytest -ra <filename>::<class>::<method>

    You can optionally specify the main executable, which is helpful if you use
    multiple virtualenvs, e.g. ::

        :call UsePyTestTestRunner("tox -e py27,py37 --")

    assuming your tox.ini has ::

        [testenv]
        commands = pytest {posargs}

    ``:call UsePyTestTestRunner(...)`` is exactly equivalent to
    ``:call pytestrunner#use("pytest", ...)`` and is provided for
    backwards compatibility.


**:call UseZopeTestRunner("bin/test")**

    Use the Zope test runner, which uses commands like ::

        bin/test -s <package> -m <module> -t '<method> (class <Class>)'

    You can optionally specify the main executable or pass additional arguments,
    e.g. ::

        :call UseZopeTestRunner("venv/bin/zope-testrunner -vv")

    ``:call UseZopeTestRunner(...)`` is exactly equivalent to
    ``:call pytestrunner#use("zope", ...)`` and is provided for
    backwards compatibility.


**:call UseNoseTestRunner("nosetests")**

    Use the nose test runner, which uses commands like ::

        nosetests <filename>:<class>.<method>

    ``:call UseNoseTestRunner(...)`` is exactly equivalent to
    ``:call pytestrunner#use("nose", ...)`` and is provided for
    backwards compatibility.


**:call UseDjangoTestRunner("bin/django test")**

    Use the Django test runner.  Assumes you're using django-nose, which uses
    commands like ::

        bin/django test <filename>:<class>.<method>

    You can optionally specify the main executable or pass additional arguments,
    e.g. ::

        :call UseDjangoTestRunner("python manage.py test")
        :call UseDjangoTestRunner("venv/bin/django-admin test")

    ``:call UseDjangoTestRunner(...)`` is exactly equivalent to
    ``:call pytestrunner#use("django", ...)`` and is provided for
    backwards compatibility.


Backwards incompatibiliy
------------------------

The following global variables are **no longer used**:


**g:pyTestRunner**

    This used to define the test runner command, instead of selecting the
    test runner configuration section.  If you keep defining it, you will
    get errors.

    Use **g:pyTestRunnerCommand** instead.


**g:pyTestRunnerTestFiltering**

    This is now completely ignored.

    Define a ``[runner:...]`` or ``[path:...]`` section with ::

        filter_for_function = -t {function}

    instead.


**g:pyTestRunnerDoctestFiltering**

    This is now completely ignored.

    Define a ``[runner:...]`` or ``[path:...]`` section with ::

        filter_for_doctest = -t {function}

    instead.

**g:pyTestRunnerTestFilteringClassAndMethodFormat**

    This is now completely ignored.

    Define a ``[runner:...]`` or ``[path:...]`` section with ::

        filter_for_method = -t {class}.{method}

    instead.


**g:pyTestRunnerTestFilteringBlacklist**

    This is now completely ignored.

    Define a ``[default]`` or ``[runner:...]`` or ``[path:...]`` section with ::

        ignore_functions_and_methods =
            __init__
            setUp
            tearDown
            test_suite

    instead.


**g:pyTestRunnerDirectoryFiltering**

    This is now completely ignored.

    Define a ``[runner:...]`` or ``[path:...]`` section with ::

        filter_for_directory = -s {directory}

    instead.

**g:pyTestRunnerFilenameFiltering**

    This is now completely ignored.

    Define a ``[runner:...]`` or ``[path:...]`` section with ::

        filter_for_file = {filename}

    instead.


**g:pyTestRunnerUseAbsoluteFilenames**

    This is now completely ignored.

    Define a ``[runner:...]`` or ``[path:...]`` section with ::

        absolute_filenames = yes

    instead.


**g:pyTestRunnerPackageFiltering**

    This is now completely ignored.

    Define a ``[runner:...]`` or ``[path:...]`` section with ::

        filter_for_package = -s {package}

    instead.


**g:pyTestRunnerModuleFiltering**

    This is now completely ignored.

    Define a ``[runner:...]`` or ``[path:...]`` section with ::

        filter_for_module = -m {module}

    instead.


**g:pyTestRunnerClipboardExtras**

    This is now completely ignored.

    Define a ``[runner:...]`` or ``[path:...]`` section with ::

        clipboard_extras = -pvc

    instead.


**g:pyTestRunnerClipboardExtrasSuffix**

    This is now completely ignored.

    Define a ``[runner:...]`` or ``[path:...]`` section with ::

        clipboard_extras_suffix = 2>&1 | less -R

    instead.


Bugs
----

- Test coverage is incomplete

- [path:...] runner=... probably overrides g:pyTestRunner, contradicting
  the documentation

- there's no error if you specify an empty command in a config file
  (or set g:pyTestRunnerCommand to a bunch of spaces)

- there's no error if a [path:...] section specifies a bad runner


Copyright
---------

``test-runner.vim`` was written by Marius Gedminas <marius@gedmin.as>.
Licence: MIT.


.. _vim-plug: https://github.com/junegunn/vim-plug
.. _asyncrun.vim: https://github.com/skywind3000/asyncrun.vim
.. _pythonhelper.vim: https://github.com/mgedmin/pythonhelper.vim
