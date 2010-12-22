from setuptools import setup

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
    install_requires = ['aml'],
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
