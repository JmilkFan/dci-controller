import os

from dci.conf import CONF


def basedir_def(*args):
    """Return an uninterpolated path relative to $pybasedir."""
    return os.path.join('$pybasedir', *args)


def bindir_def(*args):
    """Return an uninterpolated path relative to $bindir."""
    return os.path.join('$bindir', *args)


def state_path_def(*args):
    """Return an uninterpolated path relative to $state_path."""
    return os.path.join('$state_path', *args)


def basedir_rel(*args):
    """Return a path relative to $pybasedir."""
    return os.path.join(CONF.pybasedir, *args)


def bindir_rel(*args):
    """Return a path relative to $bindir."""
    return os.path.join(CONF.bindir, *args)


def state_path_rel(*args):
    """Return a path relative to $state_path."""
    return os.path.join(CONF.state_path, *args)
