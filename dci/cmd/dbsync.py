"""
Run storage database migration.
"""

import sys

from oslo_config import cfg

from dci.common.i18n import _
from dci.common import service
from dci.conf import CONF
from dci.db import migration


class DBCommand(object):

    def upgrade(self):
        migration.upgrade(CONF.command.revision)

    def revision(self):
        migration.revision(CONF.command.message, CONF.command.autogenerate)

    def stamp(self):
        migration.stamp(CONF.command.revision)

    def version(self):
        print(migration.version())

    def create_schema(self):
        migration.create_schema()


def add_command_parsers(subparsers):
    command_object = DBCommand()

    # upgrade
    parser = subparsers.add_parser(
        'upgrade',
        help=_("Upgrade the database schema to the latest version. "
               "Optionally, use --revision to specify an alembic revision "
               "string to upgrade to."))
    parser.set_defaults(func=command_object.upgrade)
    parser.add_argument('--revision', nargs='?')

    # revision
    parser = subparsers.add_parser(
        'revision',
        help=_("Create a new alembic revision. "
               "Use --message to set the message string."))
    parser.set_defaults(func=command_object.revision)
    parser.add_argument('-m', '--message')
    parser.add_argument('--autogenerate', action='store_true')

    parser = subparsers.add_parser('stamp')
    parser.set_defaults(func=command_object.stamp)
    parser.add_argument('--revision', nargs='?')

    # version
    parser = subparsers.add_parser(
        'version',
        help=_("Print the current version information and exit."))
    parser.set_defaults(func=command_object.version)

    # create_schema
    parser = subparsers.add_parser(
        'create_schema',
        help=_("Create the database schema."))
    parser.set_defaults(func=command_object.create_schema)


def main():
    command_opt = cfg.SubCommandOpt('command',
                                    title='Command',
                                    help=_('Available commands'),
                                    handler=add_command_parsers)

    CONF.register_cli_opt(command_opt)

    service.prepare_service(sys.argv)
    CONF.command.func()
