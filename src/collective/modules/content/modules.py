from collective.modules import _
from collective.relationhelpers import api as relapi
from logging import getLogger
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.multilingual.browser.interfaces import make_relation_root_path
from plone.app.textfield import RichText
from plone.app.z3cform.widget import LinkFieldWidget
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.dexterity.content import Item
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from z3c.form.browser.radio import RadioFieldWidget
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import implementer
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

log = getLogger(__name__)

text_templates = SimpleVocabulary(
    [
        SimpleTerm(value='text', title='Three columns'),
        SimpleTerm(
            value='text_expandable', title='One 2/3 column, one 1/3 column and a expandable block below'
        ),
    ]
)


class IModuleBase(model.Schema):
    """Marker Interface for all modules"""


class ITextModule(IModuleBase):
    """Dexterity-Schema for Module"""

    display_title = schema.Bool(
        title='Display title?',
        default=True,
        required=False,
    )

    text1 = RichText(
        title='Text Block 1',
        required=False,
    )

    text2 = RichText(
        title='Text Block 2',
        required=False,
    )

    text3 = RichText(
        title='Text Block 3',
        required=False,
    )

    directives.widget(template_variant=RadioFieldWidget)
    template_variant = schema.Choice(
        title='Variation',
        vocabulary=text_templates,
        required=False,
        default='text',
    )


@implementer(ITextModule)
class TextModule(Item):
    """Text Module instance class"""


simple_text_templates = SimpleVocabulary(
    [
        SimpleTerm(value='blue', title='Blue background, white text'),
        SimpleTerm(value='white', title='White background, black/blue Text'),
        SimpleTerm(value='gray', title='Gray background, black/blue Text'),
    ]
)


class ISimpleTextModule(IModuleBase):
    """Dexterity-Schema for Module"""

    text = RichText(
        title='Text',
        required=False,
    )

    image = NamedBlobImage(
        title='Image',
        required=False,
    )

    directives.widget(template_variant=RadioFieldWidget)
    template_variant = schema.Choice(
        title='Variation',
        vocabulary=simple_text_templates,
        required=False,
        default='blue',
    )


@implementer(ISimpleTextModule)
class SimpleTextModule(Item):
    """Text Module instance class"""


relationmodule_templates = SimpleVocabulary(
    [
        SimpleTerm(value='default', title=_('3 columns, no image, all items displayed')),
        SimpleTerm(value='events', title=_('2 items per row with image (events and media)')),
        SimpleTerm(value='two_item_row_without_images', title=_('2 items per row without image (press releases )')),
        SimpleTerm(value='three_item_row', title=_('3 items per row with images above each item (apropos)')),
    ]
)


class IRelationModule(IModuleBase):
    """Dexterity-Schema for Module"""

    display_title = schema.Bool(
        title='Display title?',
        default=True,
        required=False,
    )

    text = RichText(
        title='Text',
        required=False,
    )

    link_button_text = schema.TextLine(
        title='Text of Link-Button',
        default='Show all',
        required=False,
    )

    directives.widget(link=LinkFieldWidget)
    link = schema.TextLine(
        title='Link target',
        required=False,
    )

    link_text = schema.TextLine(
        title='Text for the link to each item',
        default='Read more',
        required=False,
    )

    directives.widget(template_variant=RadioFieldWidget)
    template_variant = schema.Choice(
        title='Variation',
        vocabulary=relationmodule_templates,
        required=False,
        default='default',
    )

    relations = RelationList(
        title='Anzuzeigende Inhalte',
        description='Diese Inhalte werden vor den Ergebnissen des Feldes "Suchbegriffe" angezeigt.',
        default=[],
        value_type=RelationChoice(vocabulary='plone.app.multilingual.RootCatalog'),
        required=False,
        missing_value=[],
    )
    directives.widget(
        'relations',
        RelatedItemsFieldWidget,
        vocabulary='plone.app.multilingual.RootCatalog',
        pattern_options={
            'basePath': make_relation_root_path,
        },
    )


@implementer(IRelationModule)
class RelationModule(Item):
    """Relation Module instance"""

    def items(self):
        # A list of items to display.
        results = relapi.relations(self, attribute='relations')
        collection = ICollection(self)
        if collection.query:
            collection_results = [i.getObject() for i in collection.results()]
            results += [i for i in collection_results if i not in results]
        if collection.limit and len(results) > collection.limit:
            results = results[:collection.limit]
        return results


gallerymodule_templates = SimpleVocabulary(
    [
        SimpleTerm(value='gallery', title='Default Gallery'),
    ]
)


class IGalleryModule(IModuleBase):
    """Dexterity-Schema for Module"""

    text = RichText(
        title='Text',
        required=False,
    )

    show_contained_images = schema.Bool(
        title='Show images that are inside this folder',
        required=False,
        default=True,
    )

    directives.widget(template_variant=RadioFieldWidget)
    template_variant = schema.Choice(
        title='Variation',
        vocabulary=gallerymodule_templates,
        required=False,
        default='gallery',
    )

    relations = RelationList(
        title='Anzuzeigende Bilder',
        description='Diese Inhalte werden vor den Ergebnissen des Feldes "Suchbegriffe" angezeigt.',
        default=[],
        value_type=RelationChoice(vocabulary='plone.app.multilingual.RootCatalog'),
        required=False,
        missing_value=[],
    )
    directives.widget(
        'relations',
        RelatedItemsFieldWidget,
        vocabulary='plone.app.multilingual.RootCatalog',
        pattern_options={
            'selectableTypes': ['Image'],
            # 'basePath': make_relation_root_path,
        },
    )


@implementer(IGalleryModule)
class GalleryModule(Container):
    """GalleryModule instance class"""

    def images(self):
        # A list of images to display.
        results = []
        if self.show_contained_images:
            results += self.contentValues(filter={'portal_type': 'Image'})

        results += relapi.relations(self, attribute='relations')
        collection = ICollection(self)
        if collection.query:
            collection_results = [i.getObject() for i in collection.results()]
            results += [i for i in collection_results if i not in results]
        return results


searchmodule_templates = SimpleVocabulary(
    [
        SimpleTerm(value='search', title='Facetted Navigation'),
    ]
)


class ISearchModule(IModuleBase):
    """Dexterity-Schema for Module"""

    display_title = schema.Bool(
        title='Display title?',
        default=True,
        required=False,
    )

    navigation_title = schema.TextLine(
        title='Title in Navigation',
        required=False,
    )

    text = RichText(
        title='Text',
        required=False,
    )

    directives.widget(template_variant=RadioFieldWidget)
    template_variant = schema.Choice(
        title='Variation',
        vocabulary=searchmodule_templates,
        required=False,
        default='search',
    )


@implementer(ISearchModule)
class SearchModule(Container):
    """SearchModule instance class"""


filter_templates = SimpleVocabulary(
    [
        SimpleTerm(value='filter', title='Radiobuttons'),
    ]
)


class IFilterModule(IModuleBase):
    """Dexterity-Schema for Module"""

    display_title = schema.Bool(
        title='Display title?',
        default=True,
        required=False,
    )

    navigation_title = schema.TextLine(
        title='Title in Navigation',
        required=False,
    )

    text = RichText(
        title='Text',
        required=False,
    )

    expand_button_text = schema.TextLine(
        title='Text of expand-Button',
        default='Show all',
        required=False,
    )

    link_text = schema.TextLine(
        title='Text for link',
        default='Read more',
        required=False,
    )

    image = NamedBlobImage(
        title='Image',
        required=False,
    )

    background_color = schema.Choice(
        title='Hintergrundfarbe',
        required=True,
        values=['gray', 'blue'],
        default='gray',
    )

    portaltype = schema.Choice(
        title='Inhaltstyp',
        required=True,
        default='Document',
        vocabulary='plone.app.vocabularies.UserFriendlyTypes',
    )

    searchpath_uuid = schema.Choice(
        title='Pfad zum Einschränken der Inhalte',
        vocabulary='plone.app.multilingual.RootCatalog',
        required=False,
    )
    directives.widget(
        'searchpath_uuid',
        RelatedItemsFieldWidget,
    )

    index = schema.Choice(
        title='Index zum Filtern',
        required=True,
        vocabulary='eea.faceted.vocabularies.CatalogIndexes',
    )

    vocabulary = schema.Choice(
        title='Werte aus Vocabulary',
        required=True,
        vocabulary='eea.faceted.vocabularies.PortalVocabularies',
    )

    directives.widget(template_variant=RadioFieldWidget)
    template_variant = schema.Choice(
        title='Variation',
        vocabulary=filter_templates,
        required=False,
        default='filter',
    )


@implementer(IFilterModule)
class FilterModule(Container):
    """FilterModule instance class"""


video_templates = SimpleVocabulary(
    [
        SimpleTerm(value='video', title='Show all Videos'),
        SimpleTerm(value='video_one', title='Only one Video'),
    ]
)


class IVideoModule(IModuleBase):
    """Dexterity-Schema for Module"""

    display_title = schema.Bool(
        title='Display title?',
        default=True,
        required=False,
    )

    navigation_title = schema.TextLine(
        title='Title in Navigation',
        required=False,
    )

    relations = RelationList(
        title='Anzuzeigende Videos',
        description='Diese Inhalte werden vor den Ergebnissen des Feldes "Suchbegriffe" angezeigt.',
        default=[],
        value_type=RelationChoice(vocabulary='plone.app.multilingual.RootCatalog'),
        required=False,
        missing_value=[],
    )
    directives.widget(
        'relations',
        RelatedItemsFieldWidget,
        vocabulary='plone.app.multilingual.RootCatalog',
        pattern_options={
            'basePath': make_relation_root_path,
        },
    )

    directives.widget(template_variant=RadioFieldWidget)
    template_variant = schema.Choice(
        title='Variation',
        vocabulary=video_templates,
        required=False,
        default='video',
    )


@implementer(IVideoModule)
class VideoModule(Item):
    """VideoModule instance class"""

    def items(self):
        # A list of items to display.
        results = relapi.relations(self, attribute='relations')
        collection = ICollection(self)
        if collection.query:
            collection_results = [i.getObject() for i in collection.results()]
            results += [i for i in collection_results if i not in results]
        return results


text_with_images_templates = SimpleVocabulary(
    [
        SimpleTerm(
            value='text_with_images', title='Three columns with text and images'
        ),
    ]
)


class ITextWithImagesModule(IModuleBase):
    """Dexterity-Schema for Module"""

    fieldset(
        'block1',
        label='Block 1',
        fields=['title1', 'text1', 'image1', 'link1', 'link_text1'],
    )

    fieldset(
        'block2',
        label='Block 2',
        fields=['title2', 'text2', 'image2', 'link2', 'link_text2'],
    )

    fieldset(
        'block3',
        label='Block 3',
        fields=['title3', 'text3', 'image3', 'link3', 'link_text3'],
    )

    display_title = schema.Bool(
        title='Display title?',
        default=True,
        required=False,
    )

    navigation_title = schema.TextLine(
        title='Title in Navigation',
        required=False,
    )

    image1 = NamedBlobImage(
        title='Image 1',
        required=False,
    )

    title1 = schema.TextLine(
        title='Heading Block 1',
        required=False,
    )

    text1 = schema.Text(
        title='Text Block 1',
        required=False,
    )

    directives.widget(link1=LinkFieldWidget)
    link1 = schema.TextLine(
        title='Link target for block 1',
        required=False,
    )

    link_text1 = schema.TextLine(
        title='Text for link in block 1',
        default='Read more',
        required=False,
    )

    image2 = NamedBlobImage(
        title='Image 2',
        required=False,
    )

    title2 = schema.TextLine(
        title='Heading Block 2',
        required=False,
    )

    text2 = schema.Text(
        title='Text Block 2',
        required=False,
    )

    directives.widget(link2=LinkFieldWidget)
    link2 = schema.TextLine(
        title='Link target for block 2',
        required=False,
    )

    link_text2 = schema.TextLine(
        title='Text for link in block 2',
        default='Read more',
        required=False,
    )

    image3 = NamedBlobImage(
        title='Image 3',
        required=False,
    )

    title3 = schema.TextLine(
        title='Heading Block 3',
        required=False,
    )

    text3 = schema.Text(
        title='Text Block 3',
        required=False,
    )

    directives.widget(link3=LinkFieldWidget)
    link3 = schema.TextLine(
        title='Link target for block 3',
        required=False,
    )

    link_text3 = schema.TextLine(
        title='Text for link in block 3',
        default='Read more',
        required=False,
    )

    directives.widget(template_variant=RadioFieldWidget)
    template_variant = schema.Choice(
        title='Variation',
        vocabulary=text_with_images_templates,
        required=True,
        default='text_with_images',
    )


@implementer(ITextWithImagesModule)
class TextWithImagesModule(Item):
    """Module instance class"""


banner_templates = SimpleVocabulary(
    [
        SimpleTerm(value='blue', title='Blue background, white text'),
        SimpleTerm(value='gray', title='Gray background, black/blue Text'),
        SimpleTerm(value='leibniz', title='2/3 Image, 1/3 Text with light blue background'),
    ]
)


class IBannerModule(IModuleBase):
    """Dexterity-Schema for Module"""

    display_title = schema.Bool(
        title='Display title?',
        default=True,
        required=False,
    )

    image = NamedBlobImage(
        title='Image',
        required=False,
    )

    text = RichText(
        title='Text Block',
        required=False,
    )

    directives.widget(link=LinkFieldWidget)
    link = schema.TextLine(
        title='Link target',
        required=False,
    )

    link_text = schema.TextLine(
        title='Text for link',
        default='Read more',
        required=False,
    )

    directives.widget(template_variant=RadioFieldWidget)
    template_variant = schema.Choice(
        title='Variation',
        vocabulary=banner_templates,
        required=True,
        default='blue',
    )


@implementer(IBannerModule)
class BannerModule(Item):
    """Module instance class"""
