from Acquisition import aq_get
from collective.modules.behaviors.modules import IModules
from pathlib import Path
from plone import api
from Products.GenericSetup.context import SnapshotImportContext
from Products.GenericSetup.interfaces import IBody
from zope.component import queryMultiAdapter

import os


def module_added(obj, event=None):
    # 1. Enable module for parent
    parent = obj.__parent__
    try:
        wrapped = IModules(parent)
    except TypeError:
        return
    uuid = api.content.get_uuid(obj)
    modules = list(wrapped.modules)
    if uuid not in modules:
        modules.append(uuid)
        wrapped.modules = modules

    # 2. Publish module
    api.content.transition(obj=obj, to_state='published')


def module_modified(obj, event=None):
    """Trigger reindex of page with modules after a module was changed."""
    parent = obj.__parent__
    parent.reindexObject(idxs=['SearchableText'])


def searchmodule_added(obj, event=None):
    """Configure eea for searchmodule. Unused for now."""
    view = 'faceted_subtyper'
    subtyper = api.content.get_view(view, obj, aq_get(obj, 'REQUEST'))
    if not subtyper.is_faceted:
        subtyper.enable()
        import_file = (
            Path(os.path.dirname(__file__))
            / '../profiles/default/facetednavigation/search_module.xml'
        )
        xml = import_file.read_bytes()
        environ = SnapshotImportContext(obj, 'utf-8')
        importer = queryMultiAdapter((obj, environ), IBody)
        importer.body = xml
