'''
Created on 29-jan-2010

@author: jm
'''
import unittest
from zope.testing import module
from grokcore.component.testing import grok_component
from zope.app.testing import functional
from megrok.navigation.tests import FunctionalLayer

def setUp(test):
    module.setUp(test, 'megrok.navigation.tests')

def test_suite():
    globs = {'grok_component': grok_component}
    suite = unittest.TestSuite()
    readme = functional.FunctionalDocFileSuite(
        '../README.txt', setUp=setUp, globs=globs)
    readme.layer = FunctionalLayer
    suite.addTest(readme)
    return suite