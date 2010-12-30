from sys import version_info as py_version

from setuptools import setup

requirements = ['aml']

is_py31 = (py_version.major, py_version.minor) == (3, 1)
if is_py31:
    requirements += ['argparse']

setup(
    name='roundy',
    description='a template language which is inspired by LISP and converts to HTML',
    long_description='',
    version='0.1a',
    author='Simon Liedtke',
    author_email='liedtke.simon@googlemail.com',
    url='http://pypi.python.org/pypi/roundy',
    license='WTFPL',
    py_modules=['roundy'],
    scripts=['roundy.py'],
    install_requires=requirements,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Markup'],
)
