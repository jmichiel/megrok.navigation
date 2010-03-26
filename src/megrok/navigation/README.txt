=================
megrok.navigation
=================

Megrok.navigation lets you easily add all sorts of menus to a site.
Menus are implemented as viewletmanagers, and items as viewlets.
You can also override the default templates by registering your own IPageTemplate 

Let's first setup a simple site

    >>> import grok
    >>> class MySite(grok.Container, grok.Application):
    ...     pass
    >>> grok_component('mysite', MySite)
    True

    >>> root = getRootFolder()
    >>> root['site'] = site = MySite()
    
Let us now define a menu
We'll first define an Interface, so that later on we won't need to redefine some menus after we redefined 
the Navigation menu, so this is not necessary to do, although it can lessen dependencies.

    >>> from megrok import navigation
	>>> class INavigation(navigation.interfaces.IMenu):
	...     pass
    >>> class Navigation(navigation.Menu):
    ...     grok.name('navigation')
    ...     grok.implements(INavigation)
    >>> grok_component('nav', Navigation)
    True
    
Menus are implemented as viewletmanagers

    >>> from zope.viewlet.interfaces import IViewletManager
    >>> IViewletManager.implementedBy(Navigation)
    True
    
Rendering the menu now leaves us with an empty <ul>

    >>> from zope.security.testing import Principal, Participation
    >>> from zope.security.management import newInteraction, endInteraction
    >>> participation = Participation(Principal('zope.anybody'))
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> newInteraction(participation)
    >>> nav = Navigation(site, request, grok.View(site, request))
    >>> nav.update()
    >>> len(nav.viewlets)
    0
    
    >>> print nav.render()
    <ul class="">
    </ul>
    
    
Global Menu Items
-----------------

Global Menu Items are links to fixed urls, typically links to other sites.
You define them on the menu you want them to be rendered:

    >>> class Navigation(navigation.Menu):
    ...     grok.name('navigation')
    ...     grok.implements(INavigation)
    ...     navigation.globalmenuitem('http://grok.zope.org', 'Grok!')
    >>> grok_component('nav', Navigation)
    True

Let's see what that gives us now:

    >>> nav = Navigation(site, request, grok.View(site, request))
    >>> nav.update()
    >>> len(nav.viewlets)
    1
    
    >>> print nav.render()
    <ul class="">
    <li class="">
    <a href="http://grok.zope.org">Grok!</a>
    <BLANKLINE>
    </li>    
    </ul>

You can set the css classes with the cssClass and cssItemClass attributes:

    >>> class Navigation(navigation.Menu):
    ...     grok.name('navigation')
    ...     grok.implements(INavigation)
    ...     navigation.globalmenuitem('http://grok.zope.org', 'Grok!')
    ...     cssClass='menu'
    ...     cssItemClass='menu-item'
    >>> grok_component('nav', Navigation)
    True
    >>> nav = Navigation(site, request, grok.View(site, request))
    >>> nav.update()
    >>> print nav.render()
    <ul class="menu">
    <li class="menu-item">
    <a href="http://grok.zope.org">Grok!</a>
    <BLANKLINE>
    </li>    
    </ul>


Site Menu Items
-----------------

Site menu items have links to views of the site itself, 
and are meant to be displayed for each view the menu is rendered in.
A good example is a 'Home' link to your site root.
Site Menu items are defined on the view that is to be linked to
I want to be sure that my Home link is the first.

    >>> class Index(grok.View):
    ...     grok.context(MySite)
    ...     navigation.sitemenuitem(INavigation, 'Home', order=-1)
    ...     def render(self):
    ...         return 'test'
    >>> grok_component('index', Index)
    True

Let's see what that gives us now:

    >>> nav = Navigation(site, request, grok.View(site, request))
    >>> nav.update()
    
    >>> print nav.render()
    <ul class="menu">
    <li class="menu-item">
    <a href="http://127.0.0.1/site/index">Home</a>
    <BLANKLINE>
    </li>
    <li class="menu-item">
    <a href="http://grok.zope.org">Grok!</a>
    <BLANKLINE>
    </li>
    </ul>

Contextual Menu Items
---------------------

Context menus are meant to be used to show everything you can do (all views) with the current context.
In fact all menus are context-sensitive, as a viewletmanager will only display viewlets that are appropriate for
their current context. A Menu Item defined with the :func:`menuitem` directive will inherit its context
from the view it is defined for. 
Context menus are not implemented as IBrowserMenus, but implement the same use case.
We'll first need some context to demonstrate

    >>> from zope.interface import Interface
    >>> class IFoo(Interface):
    ...     pass
    >>> class Foo(grok.Model):
    ...     grok.implements(IFoo)
    >>> site['foo'] = foo = Foo()
    >>> site['foo2'] = Foo()

We'll define a new menu as Context Menu to attach the views to

	>>> class IActions(navigation.interfaces.IMenu):
	...     pass
    >>> class Actions(navigation.Menu):
    ...     grok.implements(IActions)
    ...     grok.name('actions')
    >>> grok_component('actions', Actions)
    True
    
Now let's define some views and attach them to the menu

    >>> class FooIndex(grok.View):
    ...     grok.context(IFoo)
    ...     navigation.menuitem(IActions, 'Details', order=0)
    ...     def render(self):
    ...         return 'test'
    >>> grok_component('fooindex', FooIndex)
    True

    >>> class FooEdit(grok.View):
    ...     grok.context(IFoo)
    ...     grok.title('Edit')
    ...     navigation.menuitem(IActions, order=1)
    ...     def render(self):
    ...         return 'test'
    >>> grok_component('fooedit', FooEdit)
    True
    
Let's render it on the site:

    >>> actions = Actions(site, request, grok.View(site, request))
    >>> actions.update()
    >>> actions.viewlets
    []
    
    >>> print actions.render()
    <ul class="">
    </ul>

Since the context was the site, there were no menu items.
Let's draw it on a IFoo object:

    >>> actions = Actions(foo, request, grok.View(foo, request))
    >>> actions.update()
    >>> len(actions.viewlets)
    2
    
    >>> print actions.render()
    <ul class="">
    <li class="">
    <a href="http://127.0.0.1/site/foo/fooindex">Details</a>
    <BLANKLINE>
    </li>
    <li class="">
    <a href="http://127.0.0.1/site/foo/fooedit">Edit</a>
    <BLANKLINE>
    </li>
    </ul>
    
Note that if you don't specify a title in the menuitem directive, it will use the name
specified with the title directive, if available. Otherwise the view name is used.

Of course, you would now like to have the Actions menu be a part of our global navigation menu.
No problem: either use the submenu directive on the main menu:

    >>> class Navigation(navigation.Menu):
    ...     grok.name('navigation')
    ...     grok.implements(INavigation)
    ...     navigation.globalmenuitem('http://grok.zope.org', 'Grok!', order=10)
    ...     navigation.submenu('actions', 'Actions', order=2)
    >>> grok_component('nav', Navigation)
    True
 
    >>> nav = Navigation(foo, request, grok.View(site, request))
    >>> nav.update()
    >>> print nav.render()
    <ul class="">
    <li class="">
    <a href="http://127.0.0.1/site/index">Home</a>
    <BLANKLINE>
    </li>
    <li class="">
    <a>Actions</a>
    <ul class="">
    <li class="">
    <a href="http://127.0.0.1/site/foo/fooindex">Details</a>
    <BLANKLINE>
    </li>
    <li class="">
    <a href="http://127.0.0.1/site/foo/fooedit">Edit</a>
    <BLANKLINE>
    </li>
    </ul>
    </li>
    <li class="">
    <a href="http://grok.zope.org">Grok!</a>
    <BLANKLINE>
    </li>
    </ul>

Or use the parentmenu directive on the submenu:

First reinstate the old Navigation menu definition and the home link

    >>> class Navigation(navigation.Menu):
    ...     grok.name('navigation')
    ...     grok.implements(INavigation)
    ...     navigation.globalmenuitem('http://grok.zope.org', 'Grok!', order=10)
    >>> grok_component('nav', Navigation)
    True

Now redefine the Actions menu

    >>> class Actions(navigation.Menu):
    ...     grok.implements(IActions)
    ...     grok.name('actions')
    ...     grok.title('Actions')
    ...     navigation.parentmenu(INavigation)
    >>> grok_component('actions', Actions)
    True
 
    >>> nav = Navigation(foo, request, grok.View(site, request))
    >>> nav.update()
    >>> print nav.render()
    <ul class="">
    <li class="">
    <a href="http://127.0.0.1/site/index">Home</a>
    <BLANKLINE>
    </li>
    <li class="">
    <a>Actions</a>
    <ul class="">
    <li class="">
    <a href="http://127.0.0.1/site/foo/fooindex">Details</a>
    <BLANKLINE>
    </li>
    <li class="">
    <a href="http://127.0.0.1/site/foo/fooedit">Edit</a>
    <BLANKLINE>
    </li>
    </ul>
    </li>
    <li class="">
    <a href="http://grok.zope.org">Grok!</a>
    <BLANKLINE>
    </li>
    </ul>

Now let's throw in permissions

    >>> class FooProtected(grok.View):
    ...     grok.context(IFoo)
    ...     grok.title('Manage')
    ...     grok.require('zope.ManageContent')
    ...     navigation.menuitem(IActions, order=2)
    ...     def render(self):
    ...         return 'test'
    >>> grok_component('fooprotected', FooProtected)
    True

We shouldn't see that view

    >>> actions.update()
    >>> print actions.render()
    <ul class="">
    <li class="">
    <a href="http://127.0.0.1/site/foo/fooindex">Details</a>
    <BLANKLINE>
    </li>
    <li class="">
    <a href="http://127.0.0.1/site/foo/fooedit">Edit</a>
    <BLANKLINE>
    </li>
    </ul>

Now use a more powerful user:

    >>> from zope.security.testing import Principal, Participation
    >>> from zope.security.management import newInteraction, endInteraction
    >>> endInteraction()
    >>> participation = Participation(Principal('zope.user'))
    >>> newInteraction(participation)
    >>> actions.update()
    >>> print actions.render()
    <ul class="">
    <li class="">
    <a href="http://127.0.0.1/site/foo/fooindex">Details</a>
    <BLANKLINE>
    </li>
    <li class="">
    <a href="http://127.0.0.1/site/foo/fooedit">Edit</a>
    <BLANKLINE>
    </li>
    <li class="">
    <a href="http://127.0.0.1/site/foo/fooprotected">Manage</a>
    <BLANKLINE>
    </li>
    </ul>

You can link a view to multiple menus by repeating the menuitem directive

    >>> class FooAdd(grok.View):
    ...     grok.context(MySite)
    ...     navigation.menuitem(Actions, 'Add a Foo', order=3)
    ...     navigation.menuitem(Navigation, 'Add a Foo', order=5)
    ...     def render(self):
    ...         return 'test'
    >>> grok_component('fooadd', FooAdd)
    True

    >>> nav = Navigation(site, request, grok.View(site, request))
    >>> nav.update()
    >>> print nav.render()
    <ul class="">
    <li class="">
    <a href="http://127.0.0.1/site/index">Home</a>
    <BLANKLINE>
    </li>
    <li class="">
    <a>Actions</a>
    <ul class="">
    <li class="">
    <a href="http://127.0.0.1/site/fooadd">Add a Foo</a>
    <BLANKLINE>
    </li>
    </ul>
    </li>
    <li class="">
    <a href="http://127.0.0.1/site/fooadd">Add a Foo</a>
    <BLANKLINE>
    </li>
    <li class="">
    <a href="http://grok.zope.org">Grok!</a>
    <BLANKLINE>
    </li>
    </ul>


Content Menus
-------------

Now the icing on the cake: content menus!
Content Menus are meant to be used if you want direct links to some of your content from your menu.
A good example is a 'Products' menu that links directly to all products you offer on your site
Let's define and add some content:

    >>> from zope.schema import TextLine
    >>> class IProduct(Interface):
    ...     name = TextLine()
    >>> class Product(grok.Container):
    ...     grok.implements(IProduct)
    ...     def __init__(self, name):
    ...         super(Product, self).__init__()
    ...         self.name=name
    
    >>> site['coffeemachine']=Product('Coffee Machine')
    >>> site['terminator']=Product('Terminator')

Now the content menu. The content menu doesn't know where to get the content, so you need to override the
getContent() method. If you don't you'll get a NotImplementedError:
    
    >>> class ProductMenu(navigation.ContentMenu):
    ...     grok.name('products')    
    >>> grok_component('productmenu', ProductMenu)
    True
    >>> pm = ProductMenu(foo, request, FooIndex(foo, request))
    >>> pm.update()
    Traceback (most recent call last):
    NotImplementedError: Subclasses of ContentMenu must override getContent()

So let's define the getContent() method, and also a getTitle() method to return 
something else than the __name__ attribute. You can override the view to be rendered
with the viewName attribute, which defaults to 'index'
There is also a getURL() method that you can override to create a link yourself.

    >>> class ProductMenu(navigation.ContentMenu):
    ...     grok.name('products')
    ...     def getContent(self):
    ...         return [x for x in site.values() if IProduct.providedBy(x)]    
    ...     def getTitle(self, obj):
    ...         return obj.name    
    >>> grok_component('productmenu', ProductMenu)
    True
    >>> pm = ProductMenu(foo, request, FooIndex(foo, request))
    >>> pm.update()
    >>> print pm.render()
    <ul class="">
    <li class="">
    <a href="http://127.0.0.1/site/coffeemachine/index">Coffee Machine</a>
    <BLANKLINE>
    </li>
    <li class="">
    <a href="http://127.0.0.1/site/terminator/index">Terminator</a>
    <BLANKLINE>
    </li>
    </ul>
    
What just happened here? The items of the menu were rendered as Context Menu Items, 
with the context not the current view context, but the item to be rendered.
Why this is done like that will become clear when content submenus are thrown into the mix.
Let's define Series and Models for our Products:

    >>> class ISeries(Interface):
    ...     name = TextLine()
    >>> class Series(grok.Container):
    ...     grok.implements(ISeries)
    ...     def __init__(self, name):
    ...         super(Series, self).__init__()
    ...         self.name=name
    >>> class IModel(Interface):
    ...     name = TextLine()
    >>> class Model(grok.Container):
    ...     grok.implements(IModel)
    ...     def __init__(self, name):
    ...         super(Model, self).__init__()
    ...         self.name=name
    >>> site['terminator']['800']=Series('T-800')
    >>> site['terminator']['1000']=Series('T-1000')
    >>> site['terminator']['X']=Series('T-X')
    >>> site['terminator']['800']['101']=Model('101')

Now we need the corresponding submenus:
The ContentSubMenu class is just a ContentMenu with a default getContent method returning self.context.values()

    >>> class SeriesMenu(navigation.ContentSubMenu):
    ...     navigation.contentsubmenu('model-menu')
    ...     grok.name('series-menu')
    ...     def getTitle(self, obj):
    ...         return obj.name    
    >>> grok_component('seriesmenu', SeriesMenu)
    True
    >>> class ModelMenu(navigation.ContentSubMenu):
    ...     grok.name('model-menu')
    ...     def getTitle(self, obj):
    ...         return obj.name    
    >>> grok_component('modelmenu', ModelMenu)
    True

Now we need to link them to the product menu:

    >>> class ProductMenu(navigation.ContentMenu):
    ...     navigation.contentsubmenu('series-menu')
    ...     grok.name('products')
    ...     def getContent(self):
    ...         return [x for x in site.values() if IProduct.providedBy(x)]    
    ...     def getTitle(self, obj):
    ...         return obj.name    
    >>> grok_component('productmenu', ProductMenu)
    True

Let's render

    >>> pm = ProductMenu(site, request, grok.View(site, request))
    >>> pm.update()
    >>> print pm.render()
    <ul class="">
    <li class="">
    <a href="http://127.0.0.1/site/coffeemachine/index">Coffee Machine</a>
    <ul class="">
    </ul>
    </li>
    <li class="">
    <a href="http://127.0.0.1/site/terminator/index">Terminator</a>
    <ul class="">
    <li class="">
    <a href="http://127.0.0.1/site/terminator/1000/index">T-1000</a>
    <ul class="">
    </ul>
    </li>
    <li class="">
    <a href="http://127.0.0.1/site/terminator/800/index">T-800</a>
    <ul class="">
    <li class="">
    <a href="http://127.0.0.1/site/terminator/800/101/index">101</a>
    <BLANKLINE>
    </li>
    </ul>
    </li>
    <li class="">
    <a href="http://127.0.0.1/site/terminator/X/index">T-X</a>
    <ul class="">
    </ul>
    </li>
    </ul>
    </li>
    </ul>
        
Or we could have done it like this:

    >>> class ProductMenu(navigation.ContentMenu):
    ...     grok.name('products')
    ...     def getContent(self):
    ...         return [x for x in site.values() if IProduct.providedBy(x)]    
    ...     def getTitle(self, obj):
    ...         return obj.name    
    >>> grok_component('productmenu', ProductMenu)
    True
    >>> class SeriesMenu(navigation.ContentSubMenu):
    ...     navigation.parentmenu(ProductMenu)
    ...     grok.name('series-menu')
    ...     def getTitle(self, obj):
    ...         return obj.name    
    >>> grok_component('seriesmenu', SeriesMenu)
    True
    >>> class ModelMenu(navigation.ContentSubMenu):
    ...     navigation.parentmenu(SeriesMenu)
    ...     grok.name('model-menu')
    ...     def getTitle(self, obj):
    ...         return obj.name    
    >>> grok_component('modelmenu', ModelMenu)
    True

Let's render

    >>> pm = ProductMenu(site, request, grok.View(site, request))
    >>> pm.update()
    >>> print pm.render()
    <ul class="">
    <li class="">
    <a href="http://127.0.0.1/site/coffeemachine/index">Coffee Machine</a>
    <ul class="">
    </ul>
    </li>
    <li class="">
    <a href="http://127.0.0.1/site/terminator/index">Terminator</a>
    <ul class="">
    <li class="">
    <a href="http://127.0.0.1/site/terminator/1000/index">T-1000</a>
    <ul class="">
    </ul>
    </li>
    <li class="">
    <a href="http://127.0.0.1/site/terminator/800/index">T-800</a>
    <ul class="">
    <li class="">
    <a href="http://127.0.0.1/site/terminator/800/101/index">101</a>
    <BLANKLINE>
    </li>
    </ul>
    </li>
    <li class="">
    <a href="http://127.0.0.1/site/terminator/X/index">T-X</a>
    <ul class="">
    </ul>
    </li>
    </ul>
    </li>
    </ul>



        
Page Templates
--------------

megrok.navigation uses zope.pagetemplate (or megrok.pagetemplate) to allow you to override the default templates.
Let's define a template based on divs, instead of ul

    >>> mt = """<div tal:attributes='class viewletmanager/cssClass'>
    ... <tal:repeat tal:repeat='viewlet viewletmanager/viewlets'
    ...             tal:replace='structure viewlet/render'/>
    ... </div>"""
    >>> from megrok import pagetemplate
    >>> class DivMenu(pagetemplate.PageTemplate):
    ...     template = grok.PageTemplate(mt)
    ...     pagetemplate.view(navigation.interfaces.IMenu)
    >>> grok_component('divmenu', DivMenu)
    True

    >>> it = """<div tal:attributes='class viewletmanager/cssItemClass'>
    ... <a tal:attributes="href viewlet/link; 
    ...                    title viewlet/description|nothing">
    ... <img tal:condition="viewlet/icon | nothing" 
    ...      tal:attributes="src viewlet/icon"/>
    ... <span tal:replace="viewlet/title"/></a>
    ... <tal:replace tal:condition="viewlet/submenu | nothing" 
    ...              tal:replace="structure provider:${viewlet/submenu}"/>
    ... </div>"""
    >>> class DivMenuItem(pagetemplate.PageTemplate):
    ...     template = grok.PageTemplate(it)
    ...     pagetemplate.view(navigation.interfaces.IMenuItem)
    >>> grok_component('divmenuitem', DivMenuItem)
    True

    >>> print actions.render()
    <div class="">
    <div class="">
    <a href="http://127.0.0.1/site/foo/fooindex">
    <BLANKLINE>
    Details</a>
    <BLANKLINE>
    </div>
    <div class="">
    <a href="http://127.0.0.1/site/foo/fooedit">
    <BLANKLINE>
    Edit</a>
    <BLANKLINE>
    </div>
    <div class="">
    <a href="http://127.0.0.1/site/foo/fooprotected">
    <BLANKLINE>
    Manage</a>
    <BLANKLINE>
    </div>
    </div>
    
    
But what if you want 2 different templates for items to be used in different menus? You never specify any Items
yourself, so you can't tell them to implement a different interface and register the template to that interface.
To allow this, the :func:`itemsimplement` directive was introduced.

    >>> class IIconItem(navigation.interfaces.IMenuItem):
    ...     pass
    >>> class IconMenu(navigation.Menu):
    ...     grok.name('icons')
    ...     navigation.itemsimplement(IIconItem)
    ...     navigation.globalmenuitem('http://grok.zope.org', 'Grok!', icon='icon.jpg')
    >>> grok_component('nav', IconMenu)
    True
  
    >>> it = """<img tal:condition="viewlet/icon | nothing" 
    ...      tal:attributes="src viewlet/icon"/>"""
    >>> class IconMenuItem(pagetemplate.PageTemplate):
    ...     template = grok.PageTemplate(it)
    ...     pagetemplate.view(IIconItem)
    >>> grok_component('iconmenuitem', IconMenuItem)
    True
    >>> icons = IconMenu(site, request, grok.View(site, request))
    >>> icons.update()
    >>> print icons.render()
    <div class="">
    <img src="icon.jpg" />
    </div>
  