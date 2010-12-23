from __future__ import print_function

from os import path
import sys
sys.path.insert(0, path.pardir)

from roundy import parse_args

import pytest


def pytest_generate_tests(metafunc):
    # called once per each test function
    for funcargs in metafunc.cls.params.get(metafunc.function.__name__, ()):
        # schedule a new test function run with applied **funcargs
        metafunc.addcall(funcargs=funcargs)


class TestClass:
    # a map specifying multiple argument sets for a test method
    params = {
        'test_indent_basic': [
            dict(argv=['-i', '42']),
            dict(argv=['--indent=42']),
            dict(argv=['--indent', '42'])],
        'test_nonexistent_filename': [
            dict(argv=['-f', 'nonexistent']),
            dict(argv=['-o', 'nonexistent'])],
        'test_filename_with_directory': [
            dict(option='-f'),
            dict(option='-o')],
    }

    def test_default_args(self):
        args = parse_args([])
        assert args.filename is None
        assert args.text_attribute == 'text'
        assert args.pretty == False
        assert args.indent == 2
        assert args.outputfile is None

    def test_nonexistent_filename(self, argv, capsys):
        with pytest.raises(SystemExit):
            parse_args(argv)
        out, err = capsys.readouterr()
        assert out == u''
        assert err.strip().endswith(u'does not exist')

    def test_filename_with_directory(self, option, tmpdir, capsys):
        with pytest.raises(SystemExit):
            parse_args([option, str(tmpdir)])
        out, err = capsys.readouterr()
        assert out == u''
        assert err.strip().endswith(u'is not a file')

    def test_indent_basic(self, argv):
        args = parse_args(argv)
        assert args.indent == 42

    def test_indent_negative(self):
        args = parse_args(['-i', '-1337'])
        assert args.indent == 2
