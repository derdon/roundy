import sys

from setuptools import setup

if sys.version_info < (2, 5):
    sys.exit(
        "Fatal Error: couldn't install roundy. Reason: Python version is too "
        "low (Python2.5 or higher is required)")

# copied from
# http://lucumr.pocoo.org/2010/2/11/porting-to-python-3-a-guide/
extra = {}
if sys.version_info >= (3, 0):
    extra.update(
        use_2to3=True,
        use_2to3_fixers=['custom_fixers'])

requirements = ['distribute', 'aml']
needs_argparse = sys.version_info[:2] in [(2, 5), (2, 6), (3, 0), (3, 1)]
if needs_argparse:
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
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Markup'],
    **extra
)
