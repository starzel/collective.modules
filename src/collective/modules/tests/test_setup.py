"""Setup tests for this package."""

from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from collective.modules.testing import COLLECTIVE_MODULES_INTEGRATION_TESTING
import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that collective.modules is properly installed."""

    layer = COLLECTIVE_MODULES_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if collective.modules is installed."""
        self.assertTrue(self.installer.isProductInstalled("collective.modules"))

    def test_browserlayer(self):
        """Test that ICollectiveModulesLayer is registered."""
        from collective.modules.interfaces import ICollectiveModulesLayer
        from plone.browserlayer import utils

        self.assertIn(ICollectiveModulesLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_MODULES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstallProducts(["collective.modules"])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.modules is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled("collective.modules"))

    def test_browserlayer_removed(self):
        """Test that ICollectiveModulesLayer is removed."""
        from collective.modules.interfaces import ICollectiveModulesLayer
        from plone.browserlayer import utils

        self.assertNotIn(ICollectiveModulesLayer, utils.registered_layers())
