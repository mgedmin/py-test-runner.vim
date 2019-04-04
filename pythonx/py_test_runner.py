"""
" HACK to fore-reload it from vim with :source %
pyx 'import sys; sys.modules.pop("py_test_runner", None); import py_test_runner'  # noqa
finish
"""

import os

try:
    # Python 2
    from cStringIO import StringIO
    from ConfigParser import SafeConfigParser as ConfigParser
except ImportError:  # pragma: nocover
    # Python 3
    from io import StringIO
    from configparser import ConfigParser

try:
    import vim
except ImportError:
    vim = None


CONFIG_FILE = '~/.vim/py-test-runner.cfg'


DEFAULT_CONFIGURATION = """
[default]
runner = pytest
ignore_functions_and_methods =
    __init__
    setUp
    tearDown
    test_suite

[runner:pytest]
command = pytest -ra
filter_for_file     = {filename}
filter_for_doctest  = -k {function}
filter_for_function = {filename}::{function}
filter_for_class    = {filename}::{class}
filter_for_method   = {filename}::{class}::{method}
absolute_filenames = 1

[runner:nose]
command = nosetests
filter_for_file     = {filename}
filter_for_function = {filename}:{function}
filter_for_class    = {filename}:{class}
filter_for_method   = {filename}:{class}.{method}
absolute_filenames = 1

[runner:django]
command = bin/django test
filter_for_file     = {filename}
filter_for_function = {filename}:{function}
filter_for_class    = {filename}:{class}
filter_for_method   = {filename}:{class}.{method}
absolute_filenames = 1

[runner:zope]
command = bin/test
filter_for_package  = -s {package}
filter_for_module   = -m {module}
filter_for_function = -t {function}
filter_for_class    = -t {class}
filter_for_method   = -t '{method} [(].*[.]{class}[)]'
clipboard_extras = -pvc
"""


class RunnerConfiguration(object):

    command = ''
    filter_for_file = ''
    filter_for_directory = ''
    filter_for_package = ''
    filter_for_module = ''
    filter_for_doctest = ''
    filter_for_function = ''
    filter_for_class = ''
    filter_for_method = ''
    absolute_filenames = False
    clipboard_extras = ''
    clipboard_extras_suffix = ''
    ignore_functions_and_methods = (
        '__init__', 'setUp', 'tearDown', 'test_suite',
    )

    @staticmethod
    def clean_tag(tag):
        # Older versions of pythonhelper.vim return [fulltagname]
        # Newer versions of pythonhelper.vim return [in fulltagname (type)]
        tag = tag.strip('[]')
        if tag.startswith('in '):
            tag = tag[len('in '):]
        if tag.endswith(')'):
            tag = tag.rpartition(' (')[0]
        return tag

    @staticmethod
    def expand(template, **kwargs):
        s = template
        for k, v in kwargs.items():
            s = s.replace('{%s}' % k.strip('_'), v)
        return s

    @staticmethod
    def join(*bits):
        return ' '.join(bit for bit in bits if bit)

    @staticmethod
    def is_doctest_file(filename):
        return filename.endswith(('.txt', '.rst', '.test'))

    @staticmethod
    def is_doctest(tag):
        return not tag.startswith(('test', 'Test'))

    @staticmethod
    def is_inner_function(tag):
        return '.' in tag and tag[0].islower()

    @staticmethod
    def is_method(tag):
        return '.' in tag and tag[0].isupper()

    @staticmethod
    def is_class(tag):
        return tag[0].isupper() and '.' not in tag

    @staticmethod
    def strip_inner_function(tag):
        return tag.partition('.')[0]

    @staticmethod
    def split_class_method(tag):
        return tuple(tag.split('.')[:2])

    def is_ignored(self, name):
        return name in self.ignore_functions_and_methods

    def construct_tag_filter(self, tag):
        tag = self.clean_tag(tag)
        if not tag:
            # Should not happen.
            return ''
        if self.is_doctest(tag) and self.filter_for_doctest:
            return self.expand(self.filter_for_doctest, function=tag)
        if self.is_inner_function(tag):
            # Most likely a test that has inner functions/classes.
            tag = self.strip_inner_function(tag)
        elif self.is_method(tag):
            # Let's assume "class.method".
            class_, method = self.split_class_method(tag)
            if self.is_ignored(method):
                if self.filter_for_class:
                    return self.expand(self.filter_for_class, class_=class_)
                else:
                    tag = class_
            elif self.filter_for_method:
                return self.expand(self.filter_for_method,
                                   class_=class_, method=method)
            else:
                tag = method
        elif self.is_class(tag) and self.filter_for_class:
            # Let's assume class names start with upper case.
            return self.expand(self.filter_for_class, class_=tag)
        if self.is_ignored(tag):
            return ''
        return self.expand(self.filter_for_function, function=tag)

    def prepare_filename(self, filename):
        if self.absolute_filenames:
            filename = os.path.abspath(filename)
        return filename

    def get_module(self, filename):
        module = os.path.splitext(os.path.basename(filename))[0]
        if module == '__init__':
            return ''
        return module

    def is_package_directory(self, dirname):
        return os.path.exists(os.path.join(dirname, '__init__.py'))

    def get_package(self, filename):
        dirname = os.path.dirname(os.path.abspath(filename))
        pkg = []
        while self.is_package_directory(dirname):
            head, tail = os.path.split(dirname)
            pkg.append(tail)
            if head == dirname:
                # Who puts a __init__.py in the root directory???
                break
            dirname = head
        return '.'.join(reversed(pkg))

    def construct_doctest_file_filter(self, filename):
        return self.expand(
            self.filter_for_doctest or self.filter_for_function,
            function=os.path.basename(filename),
        )

    def construct_filter(self, filename, tag):
        filename = self.prepare_filename(filename)
        if self.is_doctest_file(filename):
            tag_filter = self.construct_doctest_file_filter(filename)
        else:
            tag_filter = self.construct_tag_filter(tag)
        if '{filename}' in tag_filter:
            return self.expand(tag_filter, filename=filename)
        else:
            directory = os.path.dirname(filename)
            module = self.get_module(filename)
            package = self.get_package(filename)
            return self.join(
                self.expand(self.filter_for_file, filename=filename),
                directory and self.expand(self.filter_for_directory,
                                          directory=directory),
                package and self.expand(self.filter_for_package,
                                        package=package),
                module and self.expand(self.filter_for_module, module=module),
                tag_filter,
            )

    def construct_command(self, filename, tag):
        filter = self.construct_filter(filename, tag)
        return self.join(self.command, filter)

    def construct_clipboard_command(self, filename, tag):
        filter = self.construct_filter(filename, tag)
        return self.join(
            self.command,
            self.clipboard_extras,
            filter,
            self.clipboard_extras_suffix,
        )


class PyTestRunner(object):

    def __init__(self, config_file=CONFIG_FILE):
        self.config = self.load_configuration(config_file)
        self.use_runner(self.config.get('default', 'runner'))

    @staticmethod
    def load_configuration(filename=CONFIG_FILE):
        cp = ConfigParser()
        cp.readfp(StringIO(DEFAULT_CONFIGURATION))
        cp.read([os.path.expanduser(filename)])
        return cp

    def use_runner(self, runner):
        section = 'runner:%s' % runner
        if not self.config.has_section(section):
            print('No [%s] section in %s' % (section, CONFIG_FILE))
            return
        self.runner = runner

    def get_option(self, section, option, default=''):
        if self.config.has_option(section, option):
            return self.config.get(section, option)
        else:
            return default

    def get_option_bool(self, section, option, default=False):
        if self.config.has_option(section, option):
            return self.config.getboolean(section, option)
        else:
            return default

    def find_overrides(self, filename):
        filename = os.path.abspath(filename)
        for section in self.config.sections():
            if section.startswith('path:'):
                sec_path = os.path.expanduser(section[len('path:'):])
                sec_path = os.path.abspath(sec_path)
                if os.path.commonprefix([sec_path, filename]) == sec_path:
                    yield section

    def get_default_runner(self, filename):
        runner = self.runner
        for section in self.find_overrides(filename):
            runner = self.get_option(section, 'runner', runner)
        return runner

    def apply_overrides(self, rc, filename):
        for section in self.find_overrides(filename):
            self.apply_config(rc, section)

    def apply_config(self, rc, section):
        rc.command = self.get_option(
            section, 'command', rc.command)
        rc.filter_for_file = self.get_option(
            section, 'filter_for_file', rc.filter_for_file)
        rc.filter_for_directory = self.get_option(
            section, 'filter_for_directory', rc.filter_for_directory)
        rc.filter_for_package = self.get_option(
            section, 'filter_for_package', rc.filter_for_package)
        rc.filter_for_module = self.get_option(
            section, 'filter_for_module', rc.filter_for_module)
        rc.filter_for_doctest = self.get_option(
            section, 'filter_for_doctest', rc.filter_for_doctest)
        rc.filter_for_function = self.get_option(
            section, 'filter_for_function', rc.filter_for_function)
        rc.filter_for_class = self.get_option(
            section, 'filter_for_class', rc.filter_for_class)
        rc.filter_for_method = self.get_option(
            section, 'filter_for_method', rc.filter_for_method)
        rc.absolute_filenames = self.get_option_bool(
            section, 'absolute_filenames', rc.absolute_filenames)
        rc.clipboard_extras = self.get_option(
            section, 'clipboard_extras', rc.clipboard_extras)
        rc.clipboard_extras_suffix = self.get_option(
            section, 'clipboard_extras_suffix', rc.clipboard_extras_suffix)
        rc.ignore_functions_and_methods = self.get_option(
            section, 'ignore_functions_and_methods',
            ' '.join(rc.ignore_functions_and_methods)).split()

    def get_runner(self, filename):
        rc = RunnerConfiguration()
        rc.ignore_functions_and_methods = self.config.get(
            'default', 'ignore_functions_and_methods').split()
        runner = self.get_default_runner(filename)
        self.apply_config(rc, 'runner:%s' % runner)
        self.apply_overrides(rc, filename)
        return rc


#
# Vim interface
#

def get_test_runner(filename):
    r = PyTestRunner()
    runner = vim.eval('g:pyTestRunner')
    if runner:
        r.use_runner(runner)
    rr = r.get_runner(filename)
    command = vim.eval('g:pyTestRunnerCommand')
    if command:
        rr.command = command
    return rr


def get_test_command(filename):
    return get_test_runner(filename).command


def get_test(filename, tag):
    return get_test_runner(filename).construct_filter(filename, tag)


def get_clipboard_command(filename, tag):
    return get_test_runner(filename).construct_clipboard_command(filename, tag)
