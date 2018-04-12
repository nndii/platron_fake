from hashlib import md5
from urllib.parse import urlunparse, urlparse
from uuid import uuid4
from xml.etree import ElementTree

from aiohttp import web


def xml_parse(data):
    result = {}

    root = ElementTree.fromstring(data)

    for child in root:
        result[child.tag] = child.text

    return result


def xml_build(root_tag, data):
    root = ElementTree.Element(root_tag)

    for key, value in data.items():
        el = ElementTree.SubElement(root, key)
        el.text = str(value)

    return b'<?xml version="1.0" encoding="utf-8"?>' + ElementTree.tostring(root)


def sign(secret, url, data):
    data['pg_salt'] = str(uuid4())
    data['pg_sig'] = _sign_create(secret, url, data)
    return data


def sign_check(secret, url, data):
    sig = _sign_create(secret, url, data)
    return data.get('pg_sig', '') == sig


def _sign_get_values(data):
    values = []
    for value in (v for k, v in sorted(data.items()) if k != 'pg_sig'):
        if isinstance(value, dict):
            values.extend(_sign_get_values(value))
        else:
            values.append(value)

    return values


def _sign_create(secret, url, data):
    script = _sign_get_script(url)

    values = [script]
    values.extend(_sign_get_values(data))
    values.append(secret)
    sig_data = ';'.join(values)

    return md5(sig_data.encode('utf8')).hexdigest()


def _sign_get_script(url):
    if url.find('/') > -1:
        path_parts = url.rsplit('/', 2)
        return path_parts[-1] or path_parts[-2]
    else:
        return url


def change_prefix(app: web.Application, url: str) -> str:
    source_url = list(urlparse(url))
    source_url[1] = urlparse(app['tc_prefix'])[1]
    return urlunparse(source_url)
