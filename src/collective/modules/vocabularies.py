from plone import api
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@provider(IVocabularyFactory)
def ModulesVocabularyFactory(context):
    terms = []
    portal_types = api.portal.get_tool('portal_types')
    module_types = [i for i in portal_types if i.endswith('module')]

    query = {
        'portal_type': module_types,
        'sort_on': 'getObjPositionInParent',
    }
    for brain in api.content.find(context=context, depth=1, **query):
        terms.append(
            SimpleTerm(
                brain.UID,
                brain.id,
                f'{brain.Title} ({brain.portal_type}: {brain.id})',
            )
        )
    return SimpleVocabulary(terms)
