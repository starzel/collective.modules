from collective.modules.behaviors.modules import IModules
from plone import api
from plone.indexer.decorator import indexer
from plone.app.textfield.value import RichTextValue


@indexer(IModules)
def searchable_text_modules(obj):
    """Triggered when a container is modified (e.g. when a module was changed)."""
    results = []
    obj = obj.aq_base
    results.append(obj.title)
    results.append(obj.description)
    results.append(' '.join([i for i in obj.Subject()]))
    transforms = api.portal.get_tool('portal_transforms')
    for item in obj.contentValues(
        filter={
            'portal_type': [
                'textmodule',
                'relationmodule',
                'videomodule',
                'gallerymodule',
                'simpletextmodule',
                'searchmodule',
                'filtermodule',
                'bannermodule',
                'textwithimagesmodule',
            ]
        }
    ):
        item = item.aq_base
        results.append(item.title)
        results.append(item.description)
        # richtext fields:
        for fieldname in ['text', 'text1', 'text2', 'text3']:
            textvalue = None
            textvalue = getattr(item, fieldname, None)
            if textvalue and isinstance(textvalue, RichTextValue):
                raw = textvalue.raw
                text = (
                    transforms.convertTo(
                        'text/plain',
                        raw,
                        mimetype=textvalue.mimeType,
                    )
                    .getData()
                    .strip()
                )
                if text:
                    results.append(text)
    return ' '.join([i for i in results if i])
