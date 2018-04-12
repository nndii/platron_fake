from urllib.parse import urljoin

import requests
from aiohttp import web

from platron_fake.resources import Transaction
from platron_fake.utils import xml_parse, sign_check, xml_build, sign


async def process_init(request: web.Request):
    params = xml_parse(request.content)
    if not sign_check(request.app['secret'], request.path, params):
        print(f'WRONG SIGNATURE')
        return None, None

    transaction = Transaction(
        **{key: value for key, value in params
           if key not in {'pg_salt', 'pg_sig'}}
    )

    request.app['t_db'][transaction.pg_payment_id] = transaction
    response_data = transaction.jsonify({'pg_payment_id', 'pg_redirect_url', 'pg_redirect_url_type'})
    response_data['pg_status'] = 'ok'

    response_data = sign(request.app['secret'], request.path, response_data)
    response = xml_build('response', response_data)
    return response, transaction


async def process_check(app: web.Application, transaction: Transaction):
    url = urljoin(app['tc_prefix'], app['check_url'])
    request_data = transaction.jsonify({
        'pg_payment_id', 'pg_order_id', 'pg_amount',
        'pg_currency', 'pg_payment_system',
        'tc_order', 'tc_payment', 'tc_tickets', 'tc_event',
        'tc_org', 'tc_vendor'
    })
    request_data = sign(app['secret'], url, request_data)
    print(f'CHECK -> {request_data}')
    response = requests.get(url, params=request_data).content
    print(f'CHECK <- {response}')
    params = xml_parse(response)
    if params['pg_status'] == 'ok':
        await process_result(app, transaction)


async def process_result(app: web.Application, transaction: Transaction):
    url = urljoin(app['tc_refix'], transaction.pg_result_url)
    request_data = transaction.jsonify()
    request_data['pg_net_amount'] = transaction.pg_amount
    request_data['pg_result'] = 1
    request_data = sign(app['secret'], url, request_data)
    print(f'CHECK -> {request_data}')
    response = requests.get(url, params=request_data).content
    print(f'CHECK <- {response}')
