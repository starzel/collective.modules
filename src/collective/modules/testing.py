from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2

import collective.modules


class CollectiveModulesLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.modules)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.modules:default")


COLLECTIVE_MODULES_FIXTURE = CollectiveModulesLayer()


COLLECTIVE_MODULES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_MODULES_FIXTURE,),
    name="CollectiveModulesLayer:IntegrationTesting",
)


COLLECTIVE_MODULES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_MODULES_FIXTURE,),
    name="CollectiveModulesLayer:FunctionalTesting",
)


COLLECTIVE_MODULES_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_MODULES_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="CollectiveModulesLayer:AcceptanceTesting",
)
