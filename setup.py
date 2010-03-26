from setuptools import setup, find_packages
from os.path import join

name='megrok.navigation'
version='0.3'

readme = open(join('src', 'megrok', 'navigation', "README.txt")).read()
history = open('HISTORY.txt').read()

install_requires = [
    'martian',
    'setuptools',
    'zope.viewlet',
    'zope.lifecycleevent',
    'zope.pagetemplate',
    'grokcore.viewlet',
    ]

tests_require = install_requires + [
    'grok',
    'zope.testing',
    'zope.testbrowser',
    'zope.contentprovider',
    'megrok.pagetemplate'
    ]

setup(
    name=name,
    version=version,
    description = 'Navigation Menus for Grok',
    long_description = '.. contents::\n\n' + readme + '\n\n=======\nHistory\n=======\n\n' + history + '\n',
    url='http://www.python.org/pypi/'+name,
    author='Jeroen Michiel',
    author_email='jmichiel@yahoo.com',
    package_dir = {'': 'src'},
    packages=find_packages('src'),
    namespace_packages=['megrok',],
    include_package_data = True,
    install_requires=install_requires,
    tests_require = tests_require,
    extras_require=dict(test = tests_require),
    platforms = 'Any',
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],   
    )
