import dci.conf
import requests


CONF = dci.conf.CONF


def mock_return_true(func):
    def return_true(*args, **kwargs):
        return True

    if CONF.api.enable_mock_for_qa:
        return return_true
    return func


def mock_return_session_from_pcf(func):
    def return_session(*args, **kwargs):
        headers = dict()
        headers['Content-Type'] = 'application/json'
        headers['Location'] = \
            'npcf-policyauthorization/v1/app-sessions/mock_app_session_id'
        session_info = requests.models.Response
        session_info.headers = headers
        return session_info

    if CONF.api.enable_mock_for_qa:
        return return_session
    return func


def mock_return_bsf_url(func):
    def return_bsf_url(*args, **kwargs):
        pcf_url = "172.18.24.10:8080"
        return pcf_url

    if CONF.api.enable_mock_for_qa:
        return return_bsf_url
    return func


def mock_return_ue_ip(func):
    def return_ue_ip(*args, **kwargs):
        ue_ip = {
            'ipv4': '127.0.0.1',
            'ipv6': '2001::1'
        }
        return ue_ip['ipv4']

    if CONF.api.enable_mock_for_ue_ip:
        return return_ue_ip
    return func


def mock_dns_rule_return_true(func):
    def return_true(*args, **kwargs):
        return True

    if CONF.api.enable_mock_for_dns_rule:
        return return_true
    return func
