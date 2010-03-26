'''
Created on 18-mrt-2010

@author: jm

    >>> root = getRootFolder()
    >>> root['site'] = site = MySite()
    >>> site['data'] = TestData()
    >>> from zope import component
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> view = component.getMultiAdapter((site, request), name='index')

Try the alternate views

    >>> menu = component.getMultiAdapter((site, request, view), name='alternateviews-menu')
    >>> menu.update()
    >>> print menu.render()
     <div id="alternateviews-menu" class="">
             <a href="http://127.0.0.1/site/index"><img src="icon.jpg" /></a>
    </div>

Check order in menus using the parentmenu directive

    >>> menu = component.getMultiAdapter((site, request, view), name='testdatamenu')
    >>> menu.update()
    >>> print menu.render()
    <ul class="">
    <li class="">
    <a>Sub Menu</a>
    <ul class="">
    </ul>  
    </li>
    <li class="">
    <a href="http://127.0.0.1/site/index">index</a>
    <BLANKLINE>
    </li>
    <li class="">
    <a href="http://127.0.0.1/site/data/index">data</a>
    <BLANKLINE>
    </li>
    </ul>  
'''
from megrok.navigation.tests import FunctionalLayer
from zope.testing import doctest
from megrok import navigation, pagetemplate
import grok
from zope.interface import Interface
from zope.app.testing.functional import getRootFolder

class ITestData(Interface):
    pass

class TestData(grok.Model):
    grok.implements(ITestData)


class MySite(grok.Container, grok.Application):
    pass


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

class TestDataMenu(navigation.ContentMenu):
    navigation.contentorder(10)
    
    def getContent(self):
        return getRootFolder()['site'].values()

class Index(grok.View):
    grok.context(MySite)
    navigation.sitemenuitem(AlternateViewMenu, icon='icon.jpg')
    navigation.sitemenuitem(TestDataMenu, order=3)
    def render(self):
        return ''



class SubMenu(navigation.Menu):
    grok.title('Sub Menu')
    navigation.parentmenu(TestDataMenu, order=2)







def test_suite():
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite
