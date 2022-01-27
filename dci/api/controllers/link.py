# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import pecan
from wsme import types as wtypes

from dci.api.controllers import base


def build_url(resource, resource_args, base_url=None):
    if base_url is None:
        base_url = pecan.request.public_url

    template = '%(url)s/v1/%(res)s'
    if resource_args:
        template += ('%(args)s'
                     if resource_args.startswith('?') else '/%(args)s')
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
    def make_link(rel_name, url, resource, resource_args, type=wtypes.Unset):
        href = build_url(resource, resource_args, base_url=url)
        return Link(href=href, rel=rel_name, type=type)

    @staticmethod
    def make_link_dict(resource, resource_args, rel='self'):
        href = build_url(resource, resource_args)
        link = {"href": href, "rel": rel}
        return link
