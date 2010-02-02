=================
megrok.navigation
=================

	>>> import grok
	>>> from zope.publisher.browser import TestRequest

Let's first setup a simple site

	>>> class MySite(grok.Container, grok.Application):
	...     pass
	>>> grok_component('mysite', MySite)
	True

	>>> root = getRootFolder()
	>>> root['site'] = site = MySite()
	>>> from zope.site.hooks import setSite
	>>> setSite(site)
	>>> request = TestRequest()
    
Let us now define a menu

	>>> from megrok import navigation
	>>> class Navigation(navigation.Menu):
	...     grok.name('navigation')
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
	<li class=""><a href="http://grok.zope.org">Grok!</a>
	<BLANKLINE>
	</li>	
	</ul>

You can set the css classes with the cssClass and cssItemClass attributes:

	>>> class Navigation(navigation.Menu):
	...     grok.name('navigation')
	...     navigation.globalmenuitem('http://grok.zope.org', 'Grok!')
	...     cssClass='menu'
	...     cssItemClass='menu-item'
	>>> grok_component('nav', Navigation)
	True
	>>> nav = Navigation(site, request, grok.View(site, request))
	>>> nav.update()
	>>> print nav.render()
	<ul class="menu">
	<li class="menu-item"><a href="http://grok.zope.org">Grok!</a>
	<BLANKLINE>
	</li>	
	</ul>


Site Menu Items
-----------------

Site menu items have links to views of the site itself, 
and are meant to be displayed for each view the menu is rendered in.
A good example is a 'Home' link to your site root.
Site Menu items are defined on the view that is to be linked to

	>>> class Index(grok.View):
	...     grok.context(MySite)
	...     navigation.sitemenuitem(Navigation, 'Home')
	...     def render(self):
	...         return 'test'
	>>> grok_component('index', Index)
	True

Let's see what that gives us now:

	>>> nav = Navigation(site, request, grok.View(site, request))
	>>> nav.update()
	
	>>> print nav.render()
	<ul class="menu">
	<li class="menu-item"><a href="http://127.0.0.1/site/index">Home</a>
	<BLANKLINE>
	</li>
	<li class="menu-item"><a href="http://grok.zope.org">Grok!</a>
	<BLANKLINE>
	</li>
	</ul>

Nice, but I want my be sure that my Home link is the first!
No problem, use the 'order' attribute in the directives to solve that,
and while where at it, let's define an icon as well

	>>> class Navigation(navigation.Menu):
	...     grok.name('navigation')
	...     navigation.globalmenuitem('http://grok.zope.org', 'Grok!', order=10)
	>>> grok_component('nav', Navigation)
	True
	>>> class Index(grok.View):
	...     grok.context(MySite)
	...     navigation.sitemenuitem(Navigation, 'Home', order=0, icon='/@@/icons/home.png')
	...     def render(self):
	...         return 'test'
	>>> grok_component('index', Index)
	True

	>>> nav = Navigation(site, request, grok.View(site, request))
	>>> nav.update()
	>>> print nav.render()
	<ul class="">
	<li class=""><a href="http://127.0.0.1/site/index"><img
	    src="/@@/icons/home.png" />Home</a>
	<BLANKLINE>
	</li>
	<li class=""><a href="http://grok.zope.org">Grok!</a>
	<BLANKLINE>
	</li>
	</ul>


Context Menus
-------------

Context menus are meant to be used to show everything you can do (all views) with the current context.
They are not implemented as IBrowserMenus, but implement the same use case.
We'll first need some context to demonstrate

	>>> from zope.interface import Interface
	>>> class IFoo(Interface):
	...     pass
	>>> class Foo(grok.Model):
	...     grok.implements(IFoo)
	>>> site['foo'] = foo = Foo()
	>>> site['foo2'] = Foo()

First we'll need to define a ContextMenu to attach the views to

	>>> class Actions(navigation.ContextMenu):
	... 	grok.name('context-menu')
	>>> grok_component('actions', Actions)
	True
	
Now let's define some views and attach them to the menu

	>>> class FooIndex(grok.View):
	...     grok.context(IFoo)
	...     navigation.menuitem(Actions, 'Details', order=0)
	...     def render(self):
	...         return 'test'
	>>> grok_component('fooindex', FooIndex)
	True

	>>> class FooEdit(grok.View):
	...     grok.context(IFoo)
	...     grok.title('Edit')
	...     navigation.menuitem(Actions, order=1)
	...     def render(self):
	...         return 'test'
	>>> grok_component('fooedit', FooEdit)
	True
	
A ContextMenu is a menu, so it's a viewletmanager:

    >>> IViewletManager.implementedBy(Actions)
    True

So it can be rendered whenever we want it:

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
	<li class=""><a href="http://127.0.0.1/site/foo/fooindex">Details</a>
	<BLANKLINE>
	</li>
	<li class=""><a href="http://127.0.0.1/site/foo/fooedit">Edit</a>
	<BLANKLINE>
	</li>
	</ul>
	
Note that if you don't specify a title in the menuitem directive, it will use the name
specified with the title directive, if available. Otherwise the view name is used.

Of course, you would now like to have the Actions menu be a part of our global navigation menu.
No problem: use the submenu directive on the main menu:

	>>> class Navigation(navigation.Menu):
	...     grok.name('navigation')
	...     navigation.globalmenuitem('http://grok.zope.org', 'Grok!')
	...     navigation.submenu('context-menu', 'Actions')
	>>> grok_component('nav', Navigation)
	True
	>>> class Index(grok.View):
	...     grok.context(MySite)
	...     navigation.sitemenuitem(Navigation, 'Home', order=0, icon='/@@/icons/home.png')
	...     def render(self):
	...         return 'test'
	>>> grok_component('index', Index)
	True
 
	>>> nav = Navigation(foo, request, grok.View(site, request))
	>>> nav.update()
	>>> print nav.render()
	<ul class="">
	<li class=""><a>Actions</a>
	<ul class="">
	<li class=""><a href="http://127.0.0.1/site/foo/fooindex">Details</a>
	<BLANKLINE>
	</li>
	<li class=""><a href="http://127.0.0.1/site/foo/fooedit">Edit</a>
	<BLANKLINE>
	</li>
	</ul>
	</li>
	<li class=""><a href="http://grok.zope.org">Grok!</a>
	<BLANKLINE>
	</li>
	<li class=""><a href="http://127.0.0.1/site/index"><img
	    src="/@@/icons/home.png" />Home</a>
	<BLANKLINE>
	</li>
	</ul>

Now let's throw in permissions

	>>> class FooProtected(grok.View):
	...     grok.context(IFoo)
	...     grok.title('Manage')
	...     grok.require('zope.ManageContent')
	...     navigation.menuitem(Actions, order=2)
	...     def render(self):
	...         return 'test'
	>>> grok_component('fooprotected', FooProtected)
	True

We shouldn't see that view

	>>> actions.update()
	>>> print actions.render()
	<ul class="">
	<li class=""><a href="http://127.0.0.1/site/foo/fooindex">Details</a>
	<BLANKLINE>
	</li>
	<li class=""><a href="http://127.0.0.1/site/foo/fooedit">Edit</a>
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
	<li class=""><a href="http://127.0.0.1/site/foo/fooindex">Details</a>
	<BLANKLINE>
	</li>
	<li class=""><a href="http://127.0.0.1/site/foo/fooedit">Edit</a>
	<BLANKLINE>
	</li>
	<li class=""><a href="http://127.0.0.1/site/foo/fooprotected">Manage</a>
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
something else the __name__ attribute. You can override the view to be rendered
with the viewName attribute, which defaults to 'index'

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
	<li class=""><a href="http://127.0.0.1/site/coffeemachine/index">Coffee Machine</a>
	<BLANKLINE>
	</li>
	<li class=""><a href="http://127.0.0.1/site/terminator/index">Terminator</a>
	<BLANKLINE>
	</li>
	</ul>
	
What just happened here? The items of the menu were rendered as ContextMenu items, 
with the context not the current view context, but the item to be rendered.
Why this is done like that wil become clear when submenus are thrown into the mix.
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
	<li class=""><a href="http://127.0.0.1/site/coffeemachine/index">Coffee Machine</a>
	<ul class="">
	</ul>
	</li>
	<li class=""><a href="http://127.0.0.1/site/terminator/index">Terminator</a>
	<ul class="">
	<li class=""><a href="http://127.0.0.1/site/terminator/1000/index">T-1000</a>
	<ul class="">
	</ul>
	</li>
	<li class=""><a href="http://127.0.0.1/site/terminator/800/index">T-800</a>
	<ul class="">
	<li class=""><a href="http://127.0.0.1/site/terminator/800/101/index">101</a>
	<BLANKLINE>
	</li>
	</ul>
	</li>
	<li class=""><a href="http://127.0.0.1/site/terminator/X/index">T-X</a>
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

	>>> menutemplate = """<div tal:attributes='class viewletmanager/cssClass'>
	... <tal:repeat tal:repeat='viewlet viewletmanager/viewlets' tal:replace='structure viewlet/render'/>
	... </div>"""
	>>> from megrok import pagetemplate
	>>> class DivMenu(pagetemplate.PageTemplate):
	...     template = grok.PageTemplate(menutemplate)
	...     pagetemplate.view(navigation.interfaces.IMenu)
	>>> grok_component('divmenu', DivMenu)
	True

	>>> itemtemplate = """<div tal:attributes='class viewletmanager/cssItemClass'><a tal:attributes="href viewlet/link; title viewlet/description|nothing"><img tal:condition="viewlet/icon | nothing" tal:attributes="src viewlet/icon"/><span tal:replace="viewlet/title"/></a>
	... <tal:replace tal:condition="viewlet/subMenu | nothing" tal:replace="structure provider:${viewlet/subMenu}"/>
	... </div>"""
	>>> class DivMenuItem(pagetemplate.PageTemplate):
	...     template = grok.PageTemplate(itemtemplate)
	...     pagetemplate.view(navigation.interfaces.IMenuItem)
	>>> grok_component('divmenuitem', DivMenuItem)
	True

	>>> print actions.render()
	<div class="">
	<div class=""><a href="http://127.0.0.1/site/foo/fooindex">Details</a>
	<BLANKLINE>
	</div>
	<div class=""><a href="http://127.0.0.1/site/foo/fooedit">Edit</a>
	<BLANKLINE>
	</div>
	<div class=""><a href="http://127.0.0.1/site/foo/fooprotected">Manage</a>
	<BLANKLINE>
	</div>
	</div>
	