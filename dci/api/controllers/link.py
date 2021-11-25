import pecan
from wsme import types as wtypes

from dci.api.controllers import base


def build_url(resource, resource_args, bookmark=False, base_url=None):
    if base_url is None:
        base_url = pecan.request.public_url

    template = '%(url)s/accelerator/%(res)s' \
        if bookmark else '%(url)s/accelerator/' + base.API_V2 + '/%(res)s'
    if resource_args:
        template += ('%(args)s' if resource_args.startswith('?')
                     else '/%(args)s')
    return template % {'url': base_url, 'res': resource, 'args': resource_args}


class Link(base.APIBase):
    """A link representation."""

    href = wtypes.text
    """The url of a link."""

    rel = wtypes.text
    """The name of a link."""

    type = wtypes.text
    """Indicates the type of document/link."""

    @staticmethod
    def make_link(rel_name, url, resource, resource_args,
                  bookmark=False, type=wtypes.Unset):
        href = build_url(resource, resource_args,
                         bookmark=bookmark, base_url=url)
        return Link(href=href, rel=rel_name, type=type)

    @staticmethod
    def make_link_dict(resource, resource_args, rel='self'):
        href = build_url(resource, resource_args)
        link = {"href": href, "rel": rel}
        return link
