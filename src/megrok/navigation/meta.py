'''
Created on 13-jan-2010

@author: jm
'''

import martian
import grokcore.viewlet
import grokcore.component
import grokcore.security

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserView
from zope.interface import Interface
from grokcore.viewlet.meta import ViewletManagerGrokker
from grokcore.view.meta.views import ViewGrokker
from grokcore.view import View
from grokcore.view.meta.views import default_view_name

from components import Menu, MenuItem, SiteMenuItem, ContextMenuItem, ContentMenu, ContentMenuItems, ContentMenuItem
from components import submenu, menuitem, sitemenuitem, globalmenuitem, contentsubmenu

from util import registerMenuItem, createClass

class MenuGrokker(ViewletManagerGrokker):
    _dynamic_items = 0
    martian.component(Menu)
    martian.directive(grokcore.viewlet.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.viewlet.name, get_default=default_view_name)
    martian.directive(submenu, name='submenus', default={})
    martian.directive(globalmenuitem, name='globalitems', default={})
    martian.directive(grokcore.viewlet.require, name='permission')

    def execute(self, factory, config, layer, name, submenus, globalitems, permission, **kw):
        for submenu, (title, order) in submenus.items():
            item_name = 'AutoMenuItem_%i'%MenuGrokker._dynamic_items
            config.action(discriminator=('viewlet', None, layer,
                             IBrowserView, factory, item_name),
                             callable=registerMenuItem,
                             args=(factory.module_info, MenuItem, (None, layer, IBrowserView, factory)
                                   , item_name, permission, 
                                   {'title':title or submenu,
                                    'subMenu': submenu},
                                    (order, MenuGrokker._dynamic_items)
                                    ))
            MenuGrokker._dynamic_items+=1
        for link, (title, order, icon) in globalitems.items():
            item_name = 'AutoMenuItem_%i'%MenuGrokker._dynamic_items
            config.action(discriminator=('viewlet', None, layer,
                             IBrowserView, factory, item_name),
                             callable=registerMenuItem,
                             args=(factory.module_info, MenuItem, (None, layer, IBrowserView, factory)
                                   , item_name, permission, 
                                   {'title':title or submenu,
                                    'link': link,
                                    'icon': icon,
                                    'subMenu': None},
                                    (order, MenuGrokker._dynamic_items)
                                    ))
            MenuGrokker._dynamic_items+=1
        return True

class ContentMenuGrokker(ViewletManagerGrokker):
    _dynamic_items = 0
    martian.component(ContentMenu)
    martian.directive(contentsubmenu, default=(None, 0))
    martian.directive(grokcore.viewlet.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.viewlet.require, name='permission')

    def execute(self, factory, config, contentsubmenu, layer, permission, **kw):
        submenu, order= contentsubmenu
        item_name = 'ContentMenuItems_%i'%ContentMenuGrokker._dynamic_items
        config.action(discriminator=('viewlet', None, layer,
                         IBrowserView, factory, item_name),
                         callable=registerMenuItem,
                         args=(factory.module_info, ContentMenuItems, (None, layer, IBrowserView, factory)
                               , item_name, permission, 
                               {'_item_class' : createClass(factory.module_info, 
                                                            ContentMenuItem, 
                                                            item_name+'_item',  
                                                            {'subMenu': submenu,
                                                             'viewName': factory.viewName}) ,
                                },
                                (order, ContentMenuGrokker._dynamic_items)
                                ))
        ContentMenuGrokker._dynamic_items+=1
        return True


class MenuViewGrokker(ViewGrokker):
    _dynamic_items = 0
    martian.priority(-1)
    martian.component(View)
    martian.directive(menuitem, name='menus', default={})
    martian.directive(sitemenuitem, name='sitemenus', default={})
    martian.directive(grokcore.viewlet.context)
    martian.directive(grokcore.viewlet.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.viewlet.require, name='permission')
    martian.directive(grokcore.viewlet.name, get_default=default_view_name)
    martian.directive(grokcore.component.title, name='viewtitle')
    martian.directive(grokcore.component.description)
    
    def execute(self, factory, config, menus, sitemenus, context, layer
                , name, viewtitle, permission, description, **kw):
        for sitemenu, (title, order, icon) in sitemenus.items():
            title = title or viewtitle or name 
            if martian.util.check_subclass(permission, grokcore.security.Permission):
                permission =  grokcore.component.name.bind().get(permission)
            item_name = 'AutoSiteMenuItem_%i'%MenuViewGrokker._dynamic_items
            config.action(discriminator=('viewlet', None, layer,
                             IBrowserView, sitemenu, item_name),
                             callable=registerMenuItem,
                             args=(factory.module_info, SiteMenuItem, (None, layer, IBrowserView, sitemenu)
                                   , item_name, permission, 
                                   {'title':title,
                                    'viewName':name,
                                    'description':description,
                                    'icon':icon
                                    },
                                    (order, MenuViewGrokker._dynamic_items)
                                    )
                             )
            MenuViewGrokker._dynamic_items+=1
        for menu, (title, order, icon) in menus.items():
            title = title or viewtitle or name
            if martian.util.check_subclass(permission, grokcore.security.Permission):
                permission =  grokcore.component.name.bind().get(permission)
            item_name = 'AutoContextMenuItem_%i'%MenuViewGrokker._dynamic_items
            config.action(discriminator=('viewlet', Interface, layer,
                             IBrowserView, menu, item_name),
                             callable=registerMenuItem,
                             args=(factory.module_info, ContextMenuItem, (context, layer, IBrowserView, menu)
                                   , item_name, permission, 
                                   {'title':title,
                                    'viewName':name, 
                                    'description':description,
                                    'icon':icon
                                    },
                                    (order, MenuViewGrokker._dynamic_items)
                                    )
                             )
            MenuViewGrokker._dynamic_items+=1
        return True


