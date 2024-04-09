from plone import api
from plone.app.contenttypes.browser.link_redirect_view import NON_RESOLVABLE_URL_SCHEMES
from plone.app.contenttypes.browser.link_redirect_view import normalize_uid_from_path
from plone.app.contenttypes.utils import replace_link_variables_by_paths
from plone.app.uuid.utils import uuidToObject
from zope.globalrequest import getRequest


def link_url(url, context, request=None):
    """Compute a absolute target URL.
    Mostly stolen from plone.app.contenttypes.browser.link_redirect_view
    """
    if not url:
        return

    if not request:
        request = getRequest()

    for scheme in NON_RESOLVABLE_URL_SCHEMES:
        if url.startswith(scheme):
            return url

    url = replace_link_variables_by_paths(context, url)

    if "resolveuid" in url:
        uid, fragment = normalize_uid_from_path(url)
        obj = uuidToObject(uid)
        if obj is None:
            # uid can't resolve, return the url
            return url

        url = obj.absolute_url()
        if fragment is not None:
            url = f"{url}{fragment}"
        return url

    if url.startswith('.'):
        context_state = api.content.get_view('@@plone_context_state', context)
        url = '/'.join([context_state.canonical_object_url(), url])
    else:
        if not url.startswith(('http://', 'https://')):
            url = request['SERVER_URL'] + url
    return url
