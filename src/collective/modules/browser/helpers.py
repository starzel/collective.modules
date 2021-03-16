from collective.modules.behaviors.modules import IModules
from collective.modules.content.modules import IGalleryModule
from plone import api
from Products.Five.browser import BrowserView

try:
    from collective.behavior.banner.banner import IBanner
    HAS_BANNER = True
except ImportError:
    HAS_BANNER = False


class ImageHelper(BrowserView):
    def image_url(self, obj, scale='preview'):
        """Get a url for a image depending on what type it is."""

        # 1. Leadimage (News Items, Images etc.)
        if getattr(obj.aq_base, 'image', None):
            return f'{obj.absolute_url()}/@@images/image/{scale}'

        # 2. Banner from collective.behavior.banner
        elif HAS_BANNER and IBanner.providedBy(obj) and obj.aq_base.banner_image:
            return f'{obj.absolute_url()}/@@images/banner_image/{scale}'

        # 3. First image from the first gallermodule
        elif IModules.providedBy(obj):
            modules_view = api.content.get_view('modules_view', obj, self.request)
            for module in modules_view.get_modules():
                if IGalleryModule.providedBy(module):
                    images = module.images()
                    if images:
                        return f'{images[0].absolute_url()}/@@images/image/{scale}'
