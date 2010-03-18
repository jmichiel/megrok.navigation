'''
Created on 18-mrt-2010

@author: jm

  >>> root = getRootFolder()
  >>> root['site'] = site = MySite()
  >>> from zope import component
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> data = TestData()
  >>> view = component.getMultiAdapter((site, request), name='index')
  >>> menu = component.getMultiAdapter((site, request, view), name='alternateviews-menu')
  >>> menu.update()
  >>> print menu.render()
   <div id="alternateviews-menu" class="">
           <a href="http://127.0.0.1/site/index"><img src="icon.jpg" /></a>
  </div>
'''
from zope.interface import Interface
from megrok.navigation.tests import FunctionalLayer
from zope.testing import doctest
from megrok import navigation, pagetemplate
import grok
from zope.app.testing.functional import getRootFolder

class MySite(grok.Container, grok.Application):
    pass


class ITestData(Interface):
    pass

class TestData(grok.Model):
    grok.implements(ITestData)

class IIconMenu(navigation.interfaces.IMenu):
    pass

class IIconMenuItem(navigation.interfaces.IMenuItem):
    pass


class AlternateViewMenu(navigation.Menu):
    grok.implements(IIconMenu)
    grok.name('alternateviews-menu')
    navigation.itemsimplement(IIconMenuItem)
    
    id='alternateviews-menu'
    
class IconMenuTemplate(pagetemplate.PageTemplate):
    grok.template('iconmenu')
    pagetemplate.view(IIconMenu)

class IconItemTemplate(pagetemplate.PageTemplate):
    grok.template('iconitem')
    pagetemplate.view(IIconMenuItem)    


class Index(grok.View):
    grok.context(grok.Application)
    navigation.sitemenuitem(AlternateViewMenu, icon='icon.jpg')
    def render(self):
        return ''







def test_suite():
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite
