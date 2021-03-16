from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from z3c.form.interfaces import IAddForm
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IModules(model.Schema):
    """Schema for Modules Behavior"""

    directives.omitted(IAddForm, 'modules')
    modules = schema.List(
        title='Modules',
        value_type=schema.Choice(vocabulary='collective.modules.container_modules'),
        required=False,
        default=[],
        missing_value=[],
    )
