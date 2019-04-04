Overview
--------

Vim script to run the tests for the current file/class/function.

Supports various Python test runners including

- pytest
- nose
- zope.testrunner
- django test


Installation
------------

I recommend vim-plug_.

You'll also need pythonhelper.vim_, and I recommend asyncrun.vim_ too.


Usage
-----

The plugin defines the following commands:


:RunTestUnderCursor

    Runs a single test function/method/class/module, depending on where your
    cursor is.  Can run the test asynchronously if you have asyncrun.vim_
    installed and have defined the ``:Make`` command `as documented in the wiki
    <https://github.com/skywind3000/asyncrun.vim/wiki/Replace-old-make-command-with-AsyncRun>`__.


:RunLastTestAgain

    Repeats the last test run.


:CopyTestUnderCursor

    Copies the command to run a single test function/method/class/module into
    the system clipboard, so you can paste it into a terminal window and not
    block your Vim instance.


Configuration
-------------

There are several functions that streamline the setup for the most common test
runners:


:call UsePyTestTestRunner(["pytest -ra"])

    Use pytest, which uses commands like ::

        pytest -ra <filename>::<class>::<method>

    You can optionally specify the main executable, which is helpful if you use
    multiple virtualenvs, e.g. ::

        :call UsePyTestTestRunner("tox -e py27,py37 --")

    assuming your tox.ini has ::

        [testenv]
        commands = pytest {posargs}


:call UseZopeTestRunner(["bin/test"])

    Use the Zope test runner, which uses commands like ::

        bin/test -s <package> -m <module> -t '<method> (class <Class>)'

    You can optionally specify the main executable or pass additional arguments,
    e.g. ::

        :call UseZopeTestRunner("venv/bin/zope-testrunner -vv")


:call UseNoseTestRunner(["nosetests"])

    Use the nose test runner, which uses commands like ::

        nosetests <filename>:<class>.<method>


:call UseDjangoTestRunner(["bin/django test"])

    Use the Django test runner.  Assumes you're using django-nose, which uses
    commands like ::

        bin/django test <filename>:<class>.<method>

    You can optionally specify the main executable or pass additional arguments,
    e.g. ::

        :call UseZopeTestRunner("python manage.py test")
        :call UseZopeTestRunner("venv/bin/django-admin test")


Manual configuration
~~~~~~~~~~~~~~~~~~~~

The following global variables are used:


g:pyVimRunCommand (default: "Make" if ":Make" exists, otherwise "make")

    Vim command to run an external process (after setting &makeprg).


g:pyTestRunner (defaukt: "bin/test")

    The main test runner command.


g:pyTestRunnerTestFiltering (default: "-t")

    Flag to filter by test method/function name.

    If your cursor is inside a function or method (according to
    pythonhelper.vim_), adds this flag followed by the function/method name
    to the command line.

    Example::

        bin/test -t doctest_something

    If you do not wish a space after the flag, use "<NOSPACE>", e.g. ::

        :let g:pyTestRunner = "bin/test"
        :let g:pyTestRunnerTestFiltering = "-t<NOSPACE>"

    would result in a command like ::

        bin/test -tdoctest_something

    when the cursor is inside a ::

        def doctest_something():
            """...

            """

    Set g:pyTestRunnerTestFiltering to a blank string to disable.

    Set g:pyTestRunnerTestFiltering to a single space if just the test name is
    enough to filter.

    Filtering by test function/method/class requires pythonhelper.vim_ to be
    installed.


g:pyTestRunnerDoctestFiltering (default: "")

    Flag to filter by test function name when it's a doctest.

    Doctests are assumed to have names starting with "doctest_".

    For example, pytest doesn't understand ``pytest testfile.py::doctest_Foo``
    so we have to do ::

        :let g:pyTestRunner = "pytest"
        :let g:pyTestRunnerDoctestFiltering = "-k"

    to get ``pytest testfile.py -k doctest_Foo``.

    Set g:pyTestRunnerDocestFiltering to a blank string to disable special
    handling for doctests (in which case g:pyTestRunnerTestFiltering will be
    used instead).


g:pyTestRunnerTestFilteringClassAndMethodFormat (default: "'{method} [(].*[.]{class}[)]'")

    Flag to filter by test class and method name.

    If your cursor is inside a method (according to pythonhelper.vim_), adds
    the g:pyTestRunnerTestFiltering flag by the class and method names
    formatted according to this setting.

    Use ``{method}` and ``{class}`` as placeholders.

    Example::

        bin/test -t 'test_something [(].*[.]TestClassName[)]'

    Filtering by test function/method/class requires pythonhelper.vim_ to be
    installed.


g:pyTestRunnerTestFilteringBlacklist (default: ["__init__", "setUp", "tearDown", "test_suite"])

    List of function/method names that are not tests.

    If your cursor is inside a function/method with one of the names listed
    here, the plugin will ignore the function/method and instead run the
    tests for the entire class/module.

    Filtering by test function/method/class requires pythonhelper.vim_ to be
    installed.


g:pyTestRunnerDirectoryFiltering (default: "")

    Flag to filter by directory name.

    Example with g:pyTestRunnerDirectoryFiltering set to "-s"::

        bin/test -s src/project/submodule/tests

    Set g:pyTestRunnerDirectoryFiltering to a blank string to disable.

    Set g:pyTestRunnerDirectoryFiltering to a single space if just the directory
    name is enough to filter.


g:pyTestRunnerFilenameFiltering (default: "")

    Flag to filter by test file name.

    Example with g:pyTestRunnerFilenameFiltering set to " "::

        bin/test src/project/submodule/tests/test_mymod.py

    Set g:pyTestRunnerFilenameFiltering to a blank string to disable.

    Set g:pyTestRunnerFilenameFiltering to a single space if just the file
    name is enough to filter.


g:pyTestRunnerUseAbsoluteFilenames (default: 0)

    If set to 1, g:pyTestRunnerUseAbsoluteFilenames will always pass absolute
    filenames to the test runner.

    This is helpful when the test runner script changes its working directory.


g:pyTestRunnerPackageFiltering (default: "")

    Flag to filter by Python package name.

    There's some logic to convert directory names to Python package names that
    relies on ``__init__.py`` files and breaks if you use PEP-420 implicit
    namespace packages.

    Example with g:pyTestRunnerPackageFiltering set to "-s"::

        bin/test -s project.submodule.tests

    Set g:pyTestRunnerPackageFiltering to a blank string to disable.

    Set g:pyTestRunnerPackageFiltering to a single space if just the directory
    name is enough to filter.


g:pyTestRunnerModuleFiltering (default: "-m")

    Flag to filter by Python module name.

    The module name is just the filename without the ``.py`` extension.

    Example with g:pyTestRunnerModuleFiltering set to "-m"::

        bin/test -m test_mod

    Set g:pyTestRunnerModuleFiltering to a blank string to disable.

    Set g:pyTestRunnerModuleFiltering to a single space if just the module
    name is enough to filter.


g:pyTestRunnerClipboardExtras (default: "-pvc")

    Additional flags to pass to the test runner when using :ClipboardTest.

    Use this to add colors or progress bars that would otherwise confuse Vim's
    :make.

    These flags are added to the beginning of the command line.


g:pyTestRunnerClipboardExtrasSuffix (default: "")

    Additional flags to pass to the test runner when using :ClipboardTest.

    Use this to add colors or progress bars that would otherwise confuse Vim's
    :make.

    These flags are added to the end of the command line.

    No shell escaping is done so you can in fact do something like ::

        :let g:pyTestRunnerClipboardExtrasSuffix = "2>&1 | less -R"

    to pipe the test runner's output to a pager.


g:pyTestLastTest (default: "")

    This is not a configuration setting, but instead the filter describing
    the last test executed via :RunTestUnderCursor.  It is used by
    :RunLastTestAgain.


Copyright
---------

``test-runner.vim`` was written by Marius Gedminas <marius@gedmin.as>.
Licence: MIT.


.. _vim-plug: https://github.com/junegunn/vim-plug
.. _asyncrun.vim: https://github.com/skywind3000/asyncrun.vim
.. _pythonhelper.vim: https://github.com/mgedmin/pythonhelper.vim
