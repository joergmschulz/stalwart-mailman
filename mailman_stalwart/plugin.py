from public import public
from zope.interface import implementer


from mailman.interfaces.plugin import IPlugin

from mailman_stalwart.rest import MTAHookREST


@public
@implementer(IPlugin)
class StalwartPlugin:
    def __init__(self):
        self.number = 0

    def pre_hook(self):
        pass

    def post_hook(self):
        pass

    @property
    def resource(self):
        return MTAHookREST()
