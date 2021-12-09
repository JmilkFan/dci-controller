import dci.conf

CONF = dci.conf.CONF


def mock_return_true(func):
    def return_true(*args, **kwargs):
        return True

    if CONF.api.enable_mock_for_qa:
        return return_true
    return func
