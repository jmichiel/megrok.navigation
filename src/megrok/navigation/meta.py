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

import components
import directives

from util import registerMenuItem, createClass



class MenuGrokker(ViewletManagerGrokker):
    _dynamic_items = 0
    martian.component(components.Menu)
    martian.directive(grokcore.viewlet.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.viewlet.name, get_default=default_view_name)
    martian.directive(grokcore.component.title, name='viewtitle')
    martian.directive(directives.submenu, name='submenus', default={})
    martian.directive(directives.contentsubmenu)
    martian.directive(directives.parentmenu, name='parentmenus', default={})
    martian.directive(directives.globalmenuitem, name='globalitems', default={})
    martian.directive(grokcore.viewlet.require, name='permission')
    martian.directive(directives.itemsimplement)
    martian.directive(directives.contentorder)
    martian.directive(directives.contentgroup)

    def execute(self, factory, config, layer, name, viewtitle, submenus, contentsubmenu, 
                parentmenus, globalitems, permission, itemsimplement, contentorder, contentgroup, **kw):
        for submenu, (title, order, group) in submenus.items():
            item_name = 'AutoMenuItem_%i'%MenuGrokker._dynamic_items
            config.action(discriminator=('viewlet', None, layer,
                             IBrowserView, factory, item_name),
                             callable=registerMenuItem,
                             args=(factory.module_info, components.MenuItem, (None, layer, IBrowserView, factory)
                                   , item_name, permission, itemsimplement,
                                   {'title':title or submenu,
                                    'submenu': submenu,
                                    'group': group},
                                    (order, MenuGrokker._dynamic_items)
                                    ))
            MenuGrokker._dynamic_items+=1
        if issubclass(factory, components.ContentSubMenu):
            for parentmenu, (title, order, icon, group) in parentmenus.items():
                parentmenu.contentsubmenu = name
        else:
            for parentmenu, (title, order, icon, group) in parentmenus.items():
                item_name = 'AutoMenuItem_%i'%MenuGrokker._dynamic_items
                title = title or viewtitle or name 
                config.action(discriminator=('viewlet', None, layer,
                                 IBrowserView, parentmenu, item_name),
                                 callable=registerMenuItem,
                                 args=(factory.module_info, components.MenuItem, (None, layer, IBrowserView, parentmenu)
                                       , item_name, permission, itemsimplement,
                                       {'title':title,
                                        'icon': icon,
                                        'submenu': name,
                                        'group': group},
                                        (order, MenuGrokker._dynamic_items)
                                        ))
                MenuGrokker._dynamic_items+=1
        if issubclass(factory, components.ContentMenu):
            contentsubmenu, group= contentsubmenu
            item_name = 'ContentMenuItems_%i'%MenuGrokker._dynamic_items
            config.action(discriminator=('viewlet', None, layer,
                             IBrowserView, factory, item_name),
                             callable=registerMenuItem,
                             args=(factory.module_info, components.ContentMenuItems, (None, layer, IBrowserView, factory)
                                   , item_name, permission, None, 
                                   {'group': group,
                                    'group':contentgroup},
                                   contentorder
                                   ))
            MenuGrokker._dynamic_items+=1
            if contentsubmenu is not None:
                factory.contentsubmenu = contentsubmenu
                
            
        for link, (title, order, icon, group) in globalitems.items():
            item_name = 'AutoMenuItem_%i'%MenuGrokker._dynamic_items
            config.action(discriminator=('viewlet', None, layer,
                             IBrowserView, factory, item_name),
                             callable=registerMenuItem,
                             args=(factory.module_info, components.MenuItem, (None, layer, IBrowserView, factory)
                                   , item_name, permission, itemsimplement,
                                   {'title':title or submenu,
                                    'link': link,
                                    'icon': icon,
                                    'submenu': None,
                                    'group': group},
                                    (order, MenuGrokker._dynamic_items)
                                    ))
            MenuGrokker._dynamic_items+=1
        return True

class MenuViewGrokker(ViewGrokker):
    _dynamic_items = 0
    martian.priority(-1)
    martian.component(View)
    martian.directive(directives.menuitem, name='menus', default={})
    martian.directive(directives.sitemenuitem, name='sitemenus', default={})
    martian.directive(grokcore.viewlet.context)
    martian.directive(grokcore.viewlet.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.viewlet.require, name='permission')
    martian.directive(grokcore.viewlet.name, get_default=default_view_name)
    martian.directive(grokcore.component.title, name='viewtitle')
    martian.directive(grokcore.component.description)
    
    def execute(self, factory, config, menus, sitemenus, context, layer
                , name, viewtitle, permission, description, **kw):
        for sitemenu, (title, order, icon, group) in sitemenus.items():
            title = title or viewtitle or name 
            if martian.util.check_subclass(permission, grokcore.security.Permission):
                permission =  grokcore.component.name.bind().get(permission)
            item_name = 'AutoSiteMenuItem_%i'%MenuViewGrokker._dynamic_items
            item_itf = directives.itemsimplement.bind().get(sitemenu)
            config.action(discriminator=('viewlet', None, layer,
                             IBrowserView, sitemenu, item_name),
                             callable=registerMenuItem,
                             args=(factory.module_info, components.SiteMenuItem, (None, layer, IBrowserView, sitemenu)
                                   , item_name, permission, item_itf, 
                                   {'title':title,
                                    'viewName':name,
                                    'description':description,
                                    'icon':icon,
                                    'group': group
                                    },
                                    (order, MenuViewGrokker._dynamic_items)
                                    )
                             )
            MenuViewGrokker._dynamic_items+=1
        for menu, (title, order, icon, group) in menus.items():
            title = title or viewtitle or name
            if martian.util.check_subclass(permission, grokcore.security.Permission):
                permission =  grokcore.component.name.bind().get(permission)
            item_name = 'AutoContextMenuItem_%i'%MenuViewGrokker._dynamic_items
            item_itf = directives.itemsimplement.bind().get(menu)
            config.action(discriminator=('viewlet', Interface, layer,
                             IBrowserView, menu, item_name),
                             callable=registerMenuItem,
                             args=(factory.module_info, components.ContextMenuItem, (context, layer, IBrowserView, menu)
                                   , item_name, permission, item_itf,
                                   {'title':title,
                                    'viewName':name, 
                                    'description':description,
                                    'icon':icon,
                                    'group': group
                                    },
                                    (order, MenuViewGrokker._dynamic_items)
                                    )
                             )
            MenuViewGrokker._dynamic_items+=1
        return True


