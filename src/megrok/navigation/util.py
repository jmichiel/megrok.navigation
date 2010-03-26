'''
Created on 28-jan-2010

@author: jm
'''
import grokcore.viewlet
from zope import component
from zope.interface import classImplements
from zope.viewlet.interfaces import IViewlet


def createClass(module_info, base, name, implements, attributes):
    bases = (base, )

    attrs = {'__view_name__': name,
             'module_info':module_info}
    if attributes:
        attrs.update(attributes)

    klass = type(name, bases, attrs)
    if implements is not None:
        classImplements(klass, implements)

    return klass


def registerMenuItem(module_info, base, adapts, name, permission, itemsimplement, attributes={}, order=(0,0)):
    klass = createClass(module_info, base, name, itemsimplement, attributes)
    grokcore.viewlet.order.set(klass, order)
    component.provideAdapter(klass, adapts, IViewlet, name)
    grokcore.viewlet.util.make_checker(klass, klass, permission, ['update', 'render'])


