import requests
from aiohttp import web
from platron_fake.resources import Transaction
from platron_fake.utils import xml_parse, sign_check, xml_build, sign, change_prefix


async def process_init(request: web.Request):
    post_params = await request.post()
    request.app['log'].debug(f'INIT <- {post_params}')
    params = xml_parse(post_params['pg_xml'])
    if not sign_check(request.app['secret'], request.path, params):
        request.app['log'].debug(f'WRONG SIGNATURE')
        return None, None

    transaction = Transaction(
        **{key: value for key, value in params.items()
           if key not in {'pg_salt', 'pg_sig'}}
    )

    request.app['t_db'][transaction.pg_payment_id] = transaction
    response_data = transaction.jsonify({'pg_payment_id', 'pg_redirect_url', 'pg_redirect_url_type'})
    response_data['pg_status'] = 'ok'

    response_data = await sign(request.app['secret'], request.path, response_data)
    response = xml_build('response', response_data)
    request.app['check'].put(transaction)
    request.app['log'].debug(f"CHECK QUEUE -> {request.app['check']}")
    return response, transaction


async def process_check(app: web.Application, transaction: Transaction):
    url = change_prefix(app, transaction.pg_check_url)
    app['log'].debug(f'CHECK URL : {url}')

    request_data = transaction.jsonify({
        'pg_payment_id', 'pg_order_id', 'pg_amount',
        'pg_currency', 'pg_payment_system',
        'tc_order', 'tc_payment', 'tc_tickets', 'tc_event',
        'tc_org', 'tc_vendor'
    })
    request_data = await sign(app['secret'], url, request_data)
    app['log'].debug(f'CHECK -> {request_data}')
    response = requests.get(url, params=request_data).content.decode()
    app['log'].debug(f'CHECK <- {response}')
    result = xml_parse(response)

    if result['pg_status'] == 'ok':
        app['result'].put(transaction)

    return result


async def process_result(app: web.Application, transaction: Transaction):
    url = change_prefix(app, transaction.pg_result_url)
    app['log'].debug(f'RESULT URL : {url}')

    request_data = transaction.jsonify()
    app['log'].debug(f'RESULT req DATA : {request_data}')
    request_data['pg_net_amount'] = transaction.pg_amount
    request_data['pg_result'] = 1
    request_data = await sign(app['secret'], url, request_data)
    app['log'].debug(f'RESULT signed req DATA : {request_data}')
    app['log'].debug(f'RESULT -> {request_data}')
    response = requests.get(url, params=request_data).content.decode()
    app['log'].debug(f'RESULT <- {response}')
    return response
