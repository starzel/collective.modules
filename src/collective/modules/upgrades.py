from plone import api
from plone.app.upgrade.utils import loadMigrationProfile

import logging

logger = logging.getLogger(__name__)

PROFILE = "profile-collective.modules:default"


def to_1001(context=None):
    portal_setup = api.portal.get_tool("portal_setup")
    logger.info(f"Update to 1001")
    loadMigrationProfile(portal_setup, "profile-collective.modules:to_1001")
