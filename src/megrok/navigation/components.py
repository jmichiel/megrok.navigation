'''
Created on 13-jan-2010

@author: jm
'''


import grokcore.viewlet, grokcore.component, grokcore.view

from zope.interface import Interface, implements
from zope.component import queryMultiAdapter
from zope.pagetemplate.interfaces import IPageTemplate
from zope import schema

try: 
    from zope.site.hooks import getSite
except ImportError:
    pass 

try: 
    # BBB stay compatible with Grok 1.0 
    from zope.app.component.hooks  import getSite
except ImportError:
    pass 

from interfaces import IMenu, IMenuItem


class BaseMenuOrItem(object):
    grokcore.component.baseclass()
    grokcore.component.context(Interface)
    
    _default_template = ''

    def render(self):
        template = getattr(self, 'template', None)
        if template:
            return self.template.render(self)
        template = queryMultiAdapter((self, self.request), IPageTemplate)
        if template is not None:
            return template()
        return grokcore.view.PageTemplateFile(self._default_template).render(self)


class Menu(BaseMenuOrItem, grokcore.viewlet.ViewletManager):
    grokcore.component.baseclass()
    implements(IMenu)
    
    _default_template = 'menu.pt'
    cssClass=''
    cssItemClass=''


class MenuItem(BaseMenuOrItem, grokcore.viewlet.Viewlet):
    grokcore.component.baseclass()
    implements(IMenuItem)

    _default_template = 'item.pt'

    link = schema.fieldproperty.FieldProperty(IMenuItem['link'])
    title = schema.fieldproperty.FieldProperty(IMenuItem['title'])
    submenu = schema.fieldproperty.FieldProperty(IMenuItem['submenu'])


class SiteMenuItem(MenuItem):
    grokcore.component.baseclass()

    @property
    def link(self):
        return self.view.url(getSite(), self.viewName)
        
        
class ContextMenuItem(MenuItem):
    grokcore.component.baseclass()

    @property
    def link(self):
        try:
            return self.view.url(self.context, self.viewName)
        except TypeError:
            return None



class ContentMenu(Menu):
    grokcore.component.baseclass()
    
    viewName='index'
    
    def getContent(self):
        raise NotImplementedError('Subclasses of ContentMenu must override getContent()')
    
    def getTitle(self, obj):
        return obj.__name__
    
    def getURL(self, obj):
        try:
            return self.view.url(obj, self.viewName)
        except TypeError:
            return None
        

    
class ContentSubMenu(ContentMenu):
    grokcore.component.baseclass()
    def getContent(self):
        return self.context.values()
            
class ContentMenuItems(MenuItem):
    grokcore.component.baseclass()
    
    def update(self):
        self.menuitems = [self._item_class(x, self.request, self.view, self.manager) for x in self.manager.getContent()]
        for i in self.menuitems:
            i.update() 
    
    def render(self):
        return u'\n'.join([item.render() for item in self.menuitems])
            
class ContentMenuItem(MenuItem):
    grokcore.component.baseclass()
    
    @property
    def title(self):
        return self.viewletmanager.getTitle(self.context)
        
    @property
    def link(self):
        return self.viewletmanager.getURL(self.context)
