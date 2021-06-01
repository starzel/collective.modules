from collective.modules.behaviors.modules import IModules
from collective.modules.utils import link_url
from plone import api
from plone.dexterity.browser.view import DefaultView
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import BoundPageTemplate
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory

try:
    from wildcard.media.interfaces import IVideoEnabled
    HAS_WILDCARD_VIDEO = True
except ImportError:
    HAS_WILDCARD_VIDEO = False


class ModulesView(BrowserView):
    """Helper for content with modules and View for Content with modules"""

    def __call__(self):
        return self.index()

    def get_modules(self):
        results = []
        try:
            wrapped = IModules(self.context)
        except TypeError:
            return results
        catalog = api.portal.get_tool('portal_catalog')
        for uid in wrapped.modules:
            brains = catalog(UID=uid)
            if len(brains) != 1:
                continue
            results.append(brains[0].getObject())
        return results

    def render_module(self, module):
        view = module.restrictedTraverse('@@inner_module')
        return view.render_core()

    def navigation(self):
        results = []
        for obj in self.get_modules():
            if getattr(obj, 'navigation_title', None):
                results.append(
                    {
                        'id': 'module_' + obj.getId(),
                        'title': obj.navigation_title,
                    }
                )
        return results


class RedirectToParent(BrowserView):
    """Used as immediate_view for all modules"""

    def __call__(self):
        parent = self.context.__parent__
        anchor = f'#module_{self.context.id}'
        self.request.response.redirect(f'{parent.absolute_url()}{anchor}')

class ModuleBaseView(DefaultView):
    def __call__(self):
        if self.__name__ == 'full_module':
            return self.index()
        return self.render_core()

    def render_core(self):
        variant = getattr(self.context, 'template_variant', None)

        if isinstance(getattr(self, variant, None), BoundPageTemplate):
            template = getattr(self, variant)
            return template()
        else:
            self.template()


class VideoModuleView(ModuleBaseView):

    video = ViewPageTemplateFile('templates/video.pt')
    video_one = ViewPageTemplateFile('templates/video_one.pt')

    def video_infos(self):
        results = []
        for obj in self.context.items():
            if not HAS_WILDCARD_VIDEO or not IVideoEnabled.providedBy(obj):
                continue
            video_view = obj.restrictedTraverse('@@wildcard_video_view')

            embed_url = video_view.get_embed_url()
            youtube_url = embed_url.replace(
                'www.youtube.com', 'www.youtube-nocookie.com'
            )

            results.append(
                {
                    'title': obj.Title(),
                    'width': obj.width,
                    'height': obj.height,
                    'youtube_url': youtube_url,
                }
            )
        return results


class TextModuleView(ModuleBaseView):

    text = ViewPageTemplateFile('templates/text.pt')
    text_one_two = ViewPageTemplateFile('templates/text_one_two.pt')
    text_expandable = ViewPageTemplateFile('templates/text_expandable.pt')
    text_full_blue = ViewPageTemplateFile('templates/text_full_blue.pt')


class TextWithImagesModuleView(ModuleBaseView):

    text_with_images = ViewPageTemplateFile('templates/text_with_images.pt')

    def link_url(self, url):
        return link_url(url, self.context, self.request)


class BannerModuleView(ModuleBaseView):

    blue = ViewPageTemplateFile('templates/banner.pt')
    gray = ViewPageTemplateFile('templates/banner.pt')

    def link_url(self, url):
        return link_url(url, self.context, self.request)


class SimpleTextModuleView(ModuleBaseView):

    blue = ViewPageTemplateFile('templates/simpletext.pt')
    white = ViewPageTemplateFile('templates/simpletext.pt')
    gray = ViewPageTemplateFile('templates/simpletext.pt')

    def image_url(self):
        if getattr(self.context.aq_base, 'image', None):
            return f'{self.context.absolute_url()}/@@images/image/preview'


class RelationModuleView(ModuleBaseView):

    default = ViewPageTemplateFile('templates/relation.pt')
    events = ViewPageTemplateFile('templates/relation_events.pt')

    def link_url(self, url):
        return link_url(url, self.context, self.request)


class GalleryModuleView(ModuleBaseView):

    gallery = ViewPageTemplateFile('templates/gallery.pt')


class SearchModuleView(ModuleBaseView):

    search = ViewPageTemplateFile('templates/search.pt')

    def search_widgets(self):
        view = api.content.get_view(
            name='facetednavigation_view',
            context=self.context,
            request=self.request,
        )
        # Return all visible widgets
        return view.get_view_widgets()


class FilterModuleView(ModuleBaseView):

    filter = ViewPageTemplateFile('templates/filter.pt')

    def results(self):
        query = {
            'portal_type': self.context.portaltype,
            'sort_on': 'getObjPositionInParent',
        }
        if self.context.searchpath_uuid:
            container = api.content.get(UID=self.context.searchpath_uuid)
            if container:
                query['path'] = {'query': '/'.join(container.getPhysicalPath())}
        portal_catalog = api.portal.get_tool('portal_catalog')
        image_helper = api.content.get_view('image_helper', self.context, self.request)
        index = portal_catalog._catalog.getIndex(self.context.index)
        results_list = []
        for brain in portal_catalog(**query):
            obj = brain.getObject()
            results_list.append(
                {
                    'title': brain.Title,
                    'uid': brain.UID,
                    'url': brain.getURL(),
                    'image_url': image_helper.image_url(obj),
                    'css_classes': ' '.join(
                        index.getEntryForObject(brain.getRID(), default=[])
                    ),
                }
            )
        return results_list

    def filter_options(self):
        portal_catalog = api.portal.get_tool('portal_catalog')
        index = self.context.index
        values = portal_catalog.uniqueValuesFor(index)
        if not self.context.vocabulary:
            return [{'value': i, 'label': i} for i in values]

        vocabulary = queryUtility(IVocabularyFactory, self.context.vocabulary, None)
        results = []
        if vocabulary:
            for term in vocabulary(self.context):
                value = term.value
                label = term.title or term.token or term.value
                results.append({'value': value, 'label': label})
        return results

    def module_image_url(self):
        if getattr(self.context.aq_base, 'image', None):
            return f'{self.context.absolute_url()}/@@images/image/preview'
