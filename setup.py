#!/usr/bin/env python

from __future__ import print_function
from setuptools import setup
from setuptools import find_packages
from setuptools.command.test import test as TestCommand
import io
import os
import sys


here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)


long_description = read('README.rst', 'HISTORY.rst')
install_requires = ['PySide']
tests_require = ['tox']


setup(
    name='qmenuview',
    version='0.1.1',
    description='PySide view for menues',
    long_description=long_description,
    author='David Zuber',
    author_email='zuber.david@gmx.de',
    url='https://github.com/storax/qmenuview',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    tests_require=tests_require,
    install_requires=install_requires,
    cmdclass={'test': Tox},
    license='BSD',
    zip_safe=False,
    keywords='qmenuview',
    test_suite='qmenuview.test.qmenuview',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ],
)
