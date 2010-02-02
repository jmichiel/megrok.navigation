'''
Created on 28-jan-2010

@author: jm
'''
import grokcore.viewlet
from zope import component
from zope.viewlet.interfaces import IViewlet


def createClass(module_info, base, name, attributes={}):
    bases = (base, )

    attrs = {'__view_name__': name,
             'module_info':module_info}
    if attributes:
        attrs.update(attributes)

    return type(name, bases, attrs)


def registerMenuItem(module_info, base, adapts, name, permission, attributes={}, order=(0,0)):
    class_ = createClass(module_info, base, name, attributes)
    grokcore.viewlet.order.set(class_, order)
    component.provideAdapter(class_, adapts, IViewlet, name)
    grokcore.viewlet.util.make_checker(class_, class_, permission, ['update', 'render'])


def registerMenu(module_info, base, adapts, name, attributes={}):
    class_ = createClass(module_info, base, name, attributes)
    component.provideAdapter(class_, adapts, IViewlet, name)


