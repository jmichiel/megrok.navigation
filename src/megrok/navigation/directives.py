'''
Created on 16-mrt-2010

@author: jm
'''
import martian
import grokcore.component
import grokcore.viewlet
from interfaces import IMenu, IMenuItem

class submenu(martian.Directive):
    scope = martian.CLASS
    store = martian.DICT
    
    def factory(self, submenu, title=None, order=0, group=''):
        if IMenu.implementedBy(submenu):
            submenu = grokcore.component.name.bind().get(submenu)
        if martian.util.not_unicode_or_ascii(submenu):
            raise martian.error.GrokImportError(
                "You can only pass a class "
                "implementing megrok.navigation.interfaces.IMenu "
                "to the '%s' directive." % self.name)
        return submenu, (title, order, group)
        
class menuitem(martian.Directive):
    scope = martian.CLASS
    store = martian.DICT
    
    def factory(self, menu, title=None, order=0, icon=None, group=''):
        martian.validateInterfaceOrClass(self, menu)
        if not (issubclass(menu, IMenu) or IMenu.implementedBy(menu)):
            raise martian.error.GrokImportError(
                "You can only pass a class implementing "
                "megrok.navigation.interfaces.IMenu "
                "to the '%s' directive." % self.name)
        return menu, (title, order, icon, group)
    
class sitemenuitem(menuitem):
    pass


class globalmenuitem(martian.Directive):
    scope = martian.CLASS
    store = martian.DICT
    
    def factory(self, link='', title=None, order=0, icon=None, group=''):
        return link, (title, order, icon, group)


class contentsubmenu(submenu):
    store = martian.ONCE
    default = (None, '')
    
    def factory(self, submenu, group=''):
        if IMenu.implementedBy(submenu):
            submenu = grokcore.component.name.bind().get(submenu)
        if martian.util.not_unicode_or_ascii(submenu):
            raise martian.error.GrokImportError(
                "You can only pass a class "
                "implementing megrok.navigation.interfaces.IMenu "
                "to the '%s' directive." % self.name)
        return submenu, group


class itemsimplement(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    validate = martian.validateInterface
    

class parentmenu(menuitem):
    pass

class contentorder(grokcore.viewlet.order):
    pass

class contentgroup(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    validate = martian.validateText
    default=''

class grouporder(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default=[]