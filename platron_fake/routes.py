import asyncio

from aiohttp import web

from platron_fake.hooks import process_init


async def pg_init(request: web.Request):
    response, transaction = await asyncio.shield(process_init(request))
    response_obj = web.Response(text=response.decode())
    response_obj.headers['Content-Type'] = 'application/xml'
    return response_obj


def setup(app):
    url = app.router

    url.add_post('/init_payment.php', pg_init)
