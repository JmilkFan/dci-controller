"""SQLAlchemy storage backend."""

import copy
import threading

from oslo_db import api as oslo_db_api
from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import enginefacade
from oslo_db.sqlalchemy import utils as sqlalchemyutils
from oslo_log import log
from oslo_utils import strutils
from oslo_utils import uuidutils
from sqlalchemy.orm.exc import NoResultFound

from dci.common import exception
from dci.common.i18n import _
from dci.db import api
from dci.db.sqlalchemy import models


_CONTEXT = threading.local()
LOG = log.getLogger(__name__)

main_context_manager = enginefacade.transaction_context()


def get_backend():
    """The backend is this module itself."""
    return Connection()


def _session_for_read():
    return enginefacade.reader.using(_CONTEXT)


def _session_for_write():
    return enginefacade.writer.using(_CONTEXT)


def get_session(use_slave=False, **kwargs):
    return main_context_manager._factory.get_legacy_facade().get_session(
        use_slave=use_slave, **kwargs)


def model_query(context, model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param context: Context of the query
    :param model: Model to query. Must be a subclass of ModelBase.
    :param args: Arguments to query. If None - model is used.

    Keyword arguments:

    :keyword project_only:
      If set to True, then will do query filter with context's project_id.
      if set to False or absent, then will not do query filter with context's
      project_id.
    :type project_only: bool
    """

    if kwargs.pop("project_only", False):
        kwargs["project_id"] = context.tenant

    with _session_for_read() as session:
        query = sqlalchemyutils.model_query(
            model, session, args, **kwargs)
        return query


def add_identity_filter(query, value):
    """Adds an identity filter to a query.

    Filters results by ID, if supplied value is a valid integer.
    Otherwise attempts to filter results by UUID.

    :param query: Initial query to add filter to.
    :param value: Value for filtering results by.
    :return: Modified query.
    """
    if strutils.is_int_like(value):
        return query.filter_by(id=value)
    elif uuidutils.is_uuid_like(value):
        return query.filter_by(uuid=value)
    else:
        raise exception.InvalidIdentity(identity=value)


def _paginate_query(context, model, query, limit=None, marker=None,
                    sort_key=None, sort_dir=None):
    sort_keys = ['uuid']
    if sort_key and sort_key not in sort_keys:
        sort_keys.insert(0, sort_key)
    try:
        query = sqlalchemyutils.paginate_query(query, model, limit, sort_keys,
                                               marker=marker,
                                               sort_dir=sort_dir)
    except db_exc.InvalidSortKey:
        raise exception.InvalidParameterValue(
            _('The sort_key value "%(key)s" is an invalid field for sorting')
            % {'key': sort_key})
    return query.all()


class Connection(api.Connection):
    """SqlAlchemy connection."""

    def __init__(self):
        pass

    # sites
    def site_get(self, context, uuid):
        query = model_query(
            context,
            models.Site).filter_by(uuid=uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ResourceNotFound(
                resource='Site',
                msg='with uuid=%s' % uuid)

    def site_list_by_filters(self, context,
                             filters, sort_key='created_at',
                             sort_dir='desc', limit=None,
                             marker=None, join_columns=None):
        """Return DCI sites that match all filters sorted by the given keys."""

        if limit == 0:
            return []

        query_prefix = model_query(context, models.Site)
        filters = copy.deepcopy(filters)

        exact_match_filter_names = ['state']

        # Filter the query
        query_prefix = self._exact_filter(models.Site, query_prefix,
                                          filters, exact_match_filter_names)
        if query_prefix is None:
            return []
        return _paginate_query(context, models.Site, query_prefix,
                               limit, marker, sort_key, sort_dir)

    def site_list(self, context, limit=None, marker=None, sort_key=None,
                  sort_dir=None):
        query = model_query(context, models.Site)
        return _paginate_query(context, models.Site, query,
                               limit, marker, sort_key, sort_dir)

    def site_update(self, context, uuid, values):
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing DCI Site.")
            raise exception.InvalidParameterValue(err=msg)

        try:
            return self._do_update_site(context, uuid, values)
        except db_exc.DBDuplicateEntry as e:
            if 'name' in e.columns:
                raise exception.DuplicateDeviceName(name=values['name'])

    def site_create(self, context, values):
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        site = models.Site()
        site.update(values)

        with _session_for_write() as session:
            try:
                session.add(site)
                session.flush()
            except db_exc.DBDuplicateEntry:
                raise exception.RecordAlreadyExists(uuid=values['uuid'])
            return site

    @oslo_db_api.retry_on_deadlock
    def _do_update_site(self, context, uuid, values):
        with _session_for_write():
            query = model_query(context, models.Site)
            query = add_identity_filter(query, uuid)
            try:
                ref = query.with_for_update().one()
            except NoResultFound:
                raise exception.ResourceNotFound(
                    resource='Site',
                    msg='with uuid=%s' % uuid)

            ref.update(values)
        return ref

    @oslo_db_api.retry_on_deadlock
    def site_delete(self, context, uuid):
        with _session_for_write():
            query = model_query(context, models.Site)
            query = add_identity_filter(query, uuid)
            count = query.delete()
            if count != 1:
                raise exception.ResourceNotFound(
                    resource='Site',
                    msg='with uuid=%s' % uuid)

    # l3evpn_dci
    def l3evpn_dci_get(self, context, uuid):
        query = model_query(
            context,
            models.L3EVPNDCI).filter_by(uuid=uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ResourceNotFound(
                resource='L3EVPNDCI',
                msg='with uuid=%s' % uuid)

    def l3evpn_dci_list_by_filters(self, context, filters,
                                   sort_key='created_at',
                                   sort_dir='desc', limit=None,
                                   marker=None, join_columns=None):
        """Return L3 EVPN DCI that match all filters sorted by the given keys.
        """

        if limit == 0:
            return []

        query_prefix = model_query(context, models.L3EVPNDCI)
        filters = copy.deepcopy(filters)

        exact_match_filter_names = ['state']

        # Filter the query
        query_prefix = self._exact_filter(models.L3EVPNDCI, query_prefix,
                                          filters, exact_match_filter_names)
        if query_prefix is None:
            return []
        return _paginate_query(context, models.L3EVPNDCI, query_prefix,
                               limit, marker, sort_key, sort_dir)

    def l3evpn_dci_list(self, context, limit=None, marker=None, sort_key=None,
                        sort_dir=None):
        query = model_query(context, models.L3EVPNDCI)
        return _paginate_query(context, models.L3EVPNDCI, query,
                               limit, marker, sort_key, sort_dir)

    def l3evpn_dci_update(self, context, uuid, values):
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing L3 EVPN DCI.")
            raise exception.InvalidParameterValue(err=msg)

        try:
            return self._do_update_l3evpn_dci(context, uuid, values)
        except db_exc.DBDuplicateEntry as e:
            if 'name' in e.columns:
                raise exception.DuplicateDeviceName(name=values['name'])

    def l3evpn_dci_create(self, context, values):
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        l3evpn_dci = models.L3EVPNDCI()
        l3evpn_dci.update(values)

        with _session_for_write() as session:
            try:
                session.add(l3evpn_dci)
                session.flush()
            except db_exc.DBDuplicateEntry:
                raise exception.RecordAlreadyExists(uuid=values['uuid'])
            return l3evpn_dci

    @oslo_db_api.retry_on_deadlock
    def _do_update_l3evpn_dci(self, context, uuid, values):
        with _session_for_write():
            query = model_query(context, models.L3EVPNDCI)
            query = add_identity_filter(query, uuid)
            try:
                ref = query.with_for_update().one()
            except NoResultFound:
                raise exception.ResourceNotFound(
                    resource='L3EVPNDCI',
                    msg='with uuid=%s' % uuid)

            ref.update(values)
        return ref

    @oslo_db_api.retry_on_deadlock
    def l3evpn_dci_delete(self, context, uuid):
        with _session_for_write():
            query = model_query(context, models.L3EVPNDCI)
            query = add_identity_filter(query, uuid)
            count = query.delete()
            if count != 1:
                raise exception.ResourceNotFound(
                    resource='L3EVPNDCI',
                    msg='with uuid=%s' % uuid)
