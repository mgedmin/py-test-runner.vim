import os

from py_test_runner import RunnerConfiguration, PyTestRunner


def test_RunnerConfiguration_clean_tag():
    clean_tag = RunnerConfiguration.clean_tag
    assert clean_tag('[foo]') == 'foo'
    assert clean_tag('[in Foo (class)]') == 'Foo'


def test_RunnerConfiguration_expand():
    expand = RunnerConfiguration.expand
    assert expand('nothing') == 'nothing'
    assert expand('{foo} + {bar} = {foobar}',
                  foo='1', bar='2', foobar='3') == '1 + 2 = 3'
    assert expand('{class}::{method}',
                  class_='Foo', method='bar') == 'Foo::bar'
    assert expand('{filename}::{class}::{method}',
                  class_='Foo', method='bar') == '{filename}::Foo::bar'


def test_RunnerConfiguration_join():
    join = RunnerConfiguration.join
    assert join() == ''
    assert join('aaa', 'bbb', 'ccc') == 'aaa bbb ccc'
    assert join('aaa', '', 'ccc') == 'aaa ccc'


def test_RunnerConfiguration_is_doctest_file():
    is_doctest_file = RunnerConfiguration.is_doctest_file
    assert is_doctest_file('foo.txt')
    assert is_doctest_file('foo.rst')
    assert is_doctest_file('foo.test')
    assert not is_doctest_file('foo.py')
    assert not is_doctest_file('foo.md')


def test_RunnerConfiguration_is_doctest():
    is_doctest = RunnerConfiguration.is_doctest
    assert is_doctest('doctest_foo')
    assert not is_doctest('test_foo')
    assert not is_doctest('TestFoo')
    assert not is_doctest('TestFoo.test_foo')
    assert not is_doctest('test_foo.something')


def test_RunnerConfiguration_is_inner_function():
    is_inner_function = RunnerConfiguration.is_inner_function
    assert not is_inner_function('doctest_foo')
    assert not is_inner_function('test_foo')
    assert not is_inner_function('TestFoo')
    assert not is_inner_function('TestFoo.test_foo')
    assert is_inner_function('test_foo.something')


def test_RunnerConfiguration_is_method():
    is_method = RunnerConfiguration.is_method
    assert not is_method('doctest_foo')
    assert not is_method('test_foo')
    assert not is_method('TestFoo')
    assert is_method('TestFoo.test_foo')
    assert not is_method('test_foo.something')


def test_RunnerConfiguration_is_class():
    is_class = RunnerConfiguration.is_class
    assert not is_class('doctest_foo')
    assert not is_class('test_foo')
    assert is_class('TestFoo')
    assert not is_class('TestFoo.test_foo')
    assert not is_class('test_foo.something')


def test_RunnerConfiguration_strip_inner_function():
    strip_inner_function = RunnerConfiguration.strip_inner_function
    assert strip_inner_function('test_foo.something') == 'test_foo'
    assert strip_inner_function('test_foo.something.more') == 'test_foo'


def test_RunnerConfiguration_split_class_method():
    spl = RunnerConfiguration.split_class_method
    assert spl('TestFoo.test_bar') == ('TestFoo', 'test_bar')
    assert spl('TestFoo.test_bar.inner') == ('TestFoo', 'test_bar')


def test_RunnerConfiguration_is_ignored():
    rc = RunnerConfiguration()
    rc.ignore_functions_and_methods = ['bad', 'beef']
    is_ignored = rc.is_ignored
    assert is_ignored('bad')
    assert not is_ignored('good')


def test_construct_tag_filter():
    rc = RunnerConfiguration()
    rc.filter_for_doctest = '-d {function}'
    rc.filter_for_function = '-f {function}'
    rc.filter_for_class = '-c {class}'
    rc.filter_for_method = '-m {class}::{method}'
    ctf = rc.construct_tag_filter
    assert ctf('test_foo') == '-f test_foo'
    assert ctf('doctest_foo') == '-d doctest_foo'
    assert ctf('TestFoo') == '-c TestFoo'
    assert ctf('TestFoo.test_bar') == '-m TestFoo::test_bar'


def test_construct_tag_filter_cleans_the_tag():
    rc = RunnerConfiguration()
    rc.filter_for_function = '-f {function}'
    ctf = rc.construct_tag_filter
    assert ctf('[in test_foo (function)]') == '-f test_foo'


def test_construct_tag_filter_no_doctest_specialization():
    rc = RunnerConfiguration()
    rc.filter_for_function = '-f {function}'
    ctf = rc.construct_tag_filter
    assert ctf('doctest_foo') == '-f doctest_foo'


def test_construct_tag_filter_no_class_specialization():
    rc = RunnerConfiguration()
    rc.filter_for_function = '-f {function}'
    ctf = rc.construct_tag_filter
    assert ctf('TestFoo') == '-f TestFoo'


def test_construct_tag_filter_no_method_specialization():
    rc = RunnerConfiguration()
    rc.filter_for_function = '-f {function}'
    ctf = rc.construct_tag_filter
    assert ctf('TestFoo.test_foo') == '-f test_foo'


def test_construct_tag_filter_inner_function_in_method():
    rc = RunnerConfiguration()
    rc.filter_for_method = '-m {class}::{method}'
    ctf = rc.construct_tag_filter
    assert ctf('TestFoo.test_bar.inner') == '-m TestFoo::test_bar'


def test_construct_tag_filter_inner_function_in_function():
    rc = RunnerConfiguration()
    rc.filter_for_function = '-f {function}'
    rc.filter_for_method = '-m {class}::{method}'
    ctf = rc.construct_tag_filter
    assert ctf('test_bar.inner') == '-f test_bar'


def test_construct_tag_filter_ignored_method():
    rc = RunnerConfiguration()
    rc.filter_for_function = '-f {function}'
    rc.filter_for_class = '-c {class}'
    rc.filter_for_method = '-m {class}::{method}'
    ctf = rc.construct_tag_filter
    assert ctf('TestFoo.__init__') == '-c TestFoo'


def test_construct_tag_filter_ignored_method_no_class_specialization():
    rc = RunnerConfiguration()
    rc.filter_for_function = '-f {function}'
    rc.filter_for_method = '-m {class}::{method}'
    ctf = rc.construct_tag_filter
    assert ctf('TestFoo.__init__') == '-f TestFoo'


def test_construct_tag_filter_ignored_function():
    rc = RunnerConfiguration()
    rc.filter_for_function = '-f {function}'
    ctf = rc.construct_tag_filter
    assert ctf('setUp') == ''


def test_construct_tag_filter_no_configuration():
    rc = RunnerConfiguration()
    ctf = rc.construct_tag_filter
    assert ctf('test_foo') == ''


def test_construct_tag_filter_no_tag():
    rc = RunnerConfiguration()
    rc.filter_for_function = '-f {function}'
    ctf = rc.construct_tag_filter
    assert ctf('') == ''
    assert ctf('[]') == ''


def test_prepare_filename():
    rc = RunnerConfiguration()
    assert rc.prepare_filename('foo.py') == 'foo.py'
    rc.absolute_filenames = True
    assert rc.prepare_filename('foo.py') == os.path.abspath('foo.py')


def test_get_module():
    rc = RunnerConfiguration()
    assert rc.get_module('foo.py') == 'foo'
    assert rc.get_module('foo/bar.py') == 'bar'
    assert rc.get_module('foo/__init__.py') == ''


def test_get_package():
    rc = RunnerConfiguration()
    rc.is_package_directory = lambda d: (
        os.path.relpath(d).replace(os.path.sep, '/') in (
            'src/pkg',
            'src/pkg/sub',
        )
    )
    assert rc.get_package('src/foo.py') == ''
    assert rc.get_package('src/pkg/foo.py') == 'pkg'
    assert rc.get_package('src/pkg/sub/foo.py') == 'pkg.sub'
    assert rc.get_package('src/pkg/sub/__init__.py') == 'pkg.sub'


def test_get_package_no_infinite_loop_in_perverse_configs():
    rc = RunnerConfiguration()
    rc.is_package_directory = lambda d: True
    rc.get_package('foo.py')


def test_construct_filter_no_tag():
    rc = RunnerConfiguration()
    rc.filter_for_file = '-F {filename}'
    rc.filter_for_function = '-f {function}'
    cf = rc.construct_filter
    assert cf('test_foo.py', '') == '-F test_foo.py'
    assert cf('test_foo.py', 'setUp') == '-F test_foo.py'


def test_construct_filter_with_tag():
    rc = RunnerConfiguration()
    rc.filter_for_file = '-F {filename}'
    rc.filter_for_function = '-f {function}'
    cf = rc.construct_filter
    assert cf('test_foo.py', 'test_bar') == '-F test_foo.py -f test_bar'


def test_construct_filter_with_tag_combined():
    rc = RunnerConfiguration()
    rc.filter_for_file = '-F {filename}'
    rc.filter_for_function = '{filename}::{function}'
    cf = rc.construct_filter
    assert cf('test_foo.py', 'test_bar') == 'test_foo.py::test_bar'


def test_construct_filter_absolute_filename():
    rc = RunnerConfiguration()
    rc.filter_for_file = '-F {filename}'
    rc.absolute_filenames = True
    cf = rc.construct_filter
    assert cf('test_foo.py', '') == '-F ' + os.path.abspath('test_foo.py')


def test_construct_filter_with_module():
    rc = RunnerConfiguration()
    rc.filter_for_module = '-m {module}'
    rc.filter_for_function = '-t {function}'
    cf = rc.construct_filter
    assert cf('pkg/test_foo.py', 'test_bar') == '-m test_foo -t test_bar'


def test_construct_filter_with_module_ignores_init():
    rc = RunnerConfiguration()
    rc.filter_for_module = '-m {module}'
    rc.filter_for_function = '-t {function}'
    cf = rc.construct_filter
    assert cf('pkg/__init__.py', 'test_bar') == '-t test_bar'


def test_construct_filter_with_package():
    rc = RunnerConfiguration()
    rc.filter_for_package = '-p {package}'
    rc.filter_for_module = '-m {module}'
    rc.filter_for_function = '-t {function}'
    rc.is_package_directory = lambda d: (
        os.path.relpath(d).replace(os.path.sep, '/') == 'pkg'
    )
    cf = rc.construct_filter
    assert cf('pkg/test_foo.py', 'test_bar') == (
        '-p pkg -m test_foo -t test_bar'
    )


def test_construct_filter_with_directory():
    rc = RunnerConfiguration()
    rc.filter_for_directory = '-d {directory}'
    rc.filter_for_module = '-m {module}'
    rc.filter_for_function = '-t {function}'
    cf = rc.construct_filter
    assert cf('pkg/test_foo.py', 'test_bar') == (
        '-d pkg -m test_foo -t test_bar'
    )
    assert cf('test_foo.py', 'test_bar') == (
        '-m test_foo -t test_bar'
    )


def test_construct_filter_with_directory_when_using_absolute_filenames():
    rc = RunnerConfiguration()
    rc.filter_for_directory = '-d {directory}'
    rc.filter_for_module = '-m {module}'
    rc.filter_for_function = '-t {function}'
    rc.absolute_filenames = True
    cf = rc.construct_filter
    assert cf('pkg/test_foo.py', 'test_bar') == (
        '-d %s -m test_foo -t test_bar' % os.path.abspath('pkg')
    )


def test_construct_filter_doctest_file():
    rc = RunnerConfiguration()
    rc.filter_for_doctest = '-d {function}'
    rc.filter_for_function = '-t {function}'
    cf = rc.construct_filter
    assert cf('doctests/test.txt', '') == '-d test.txt'


def test_construct_filter_doctest_file_no_explicit_doctest_config():
    rc = RunnerConfiguration()
    rc.filter_for_function = '-t {function}'
    cf = rc.construct_filter
    assert cf('doctests/test.txt', '') == '-t test.txt'


def test_construct_command():
    rc = RunnerConfiguration()
    rc.command = 'pytest -ra'
    rc.filter_for_function = '{filename}::{function}'
    cc = rc.construct_command
    assert cc('test_foo.py', 'test_bar') == 'pytest -ra test_foo.py::test_bar'


def test_construct_clipboard_command():
    rc = RunnerConfiguration()
    rc.command = 'pytest -ra'
    rc.filter_for_function = '{filename}::{function}'
    rc.clipboard_extras = '--color=auto'
    rc.clipboard_extras_suffix = '2>&1 | less -R'
    ccc = rc.construct_clipboard_command
    assert ccc('test_foo.py', 'test_bar') == (
        'pytest -ra --color=auto test_foo.py::test_bar 2>&1 | less -R'
    )


def test_construct_clipboard_command_no_extras():
    rc = RunnerConfiguration()
    rc.command = 'pytest -ra'
    rc.filter_for_function = '{filename}::{function}'
    rc.clipboard_extras = ''
    rc.clipboard_extras_suffix = ''
    ccc = rc.construct_clipboard_command
    assert ccc('test_foo.py', 'test_bar') == (
        'pytest -ra test_foo.py::test_bar'
    )


def test_load_configuration():
    cp = PyTestRunner.load_configuration('/dev/null')
    assert cp.get('default', 'runner') == 'pytest'
    assert cp.get('runner:pytest', 'command') == 'pytest -ra'


def test_use_runner_good():
    ptr = PyTestRunner('/dev/null')
    ptr.use_runner("zope")
    assert ptr.runner == "zope"


def test_use_runner_bad():
    ptr = PyTestRunner('/dev/null')
    ptr.use_runner("nosuch")
    assert ptr.runner == "pytest"


def test_get_runner():
    ptr = PyTestRunner('/dev/null')
    rc = ptr.get_runner('')
    rc.absolute_filenames = False  # makes the test easier
    assert rc.construct_command('foo.py', 'doctest_bar') == (
        'pytest -ra foo.py -k doctest_bar'
    )


def test_use_runner():
    ptr = PyTestRunner('/dev/null')
    ptr.use_runner('zope')
    rc = ptr.get_runner('')
    assert rc.construct_command('foo.py', 'doctest_bar') == (
        'bin/test -m foo -t doctest_bar'
    )
