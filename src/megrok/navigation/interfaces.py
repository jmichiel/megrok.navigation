'''
Created on 13-jan-2010

@author: jm
'''

from zope.viewlet.interfaces import IViewletManager, IViewlet
from zope import schema
from zope.interface import Interface

class IMenu(IViewletManager):
    "Menus are viewletmanagers"
    
    
class IMenuItem(IViewlet):
    "Menu items are viewlets"
    link = schema.URI()
    title = schema.TextLine()
    submenu = schema.TextLine()
    