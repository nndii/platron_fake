import asyncio
import logging
import os
import sys
from queue import Queue

from aiohttp import web
from platron_fake.hooks import process_check, process_result
from platron_fake.routes import setup

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)7s: %(message)s',
    stream=sys.stdout,
)


async def check_task(app: web.Application):
    try:
        await asyncio.sleep(0.01)
        while True:
            if not app['check'].empty():
                app['log'].debug('PROCESS CHECK RUNNING')
                result = await process_check(app, app['check'].get())
                app['log'].debug(f'CHECK FINIFSHED <- {result}')
            await asyncio.sleep(1.5)
    except asyncio.CancelledError:
        app['log'].debug('Cancel ipn listener..')


async def result_task(app: web.Application):
    try:
        await asyncio.sleep(0.01)
        while True:
            if not app['result'].empty():
                app['log'].debug('PROCESS RESULT RUNNING')
                result = await process_result(app, app['result'].get())
                app['log'].debug(f'RESULT FINIFSHED <- {result}')
            await asyncio.sleep(1.5)
    except asyncio.CancelledError:
        app['log'].debug('Cancel result listener..')


async def start_bg_tasks(app: web.Application):
    app['check_task_'] = app.loop.create_task(check_task(app))
    app['result_task_'] = app.loop.create_task(result_task(app))


async def cleanup_bg_tasks(app: web.Application):
    app['log'].debug('cleanup background tasks')
    app['check_task_'].cancel()
    app['result_task_'].cancel()


def create_app() -> web.Application:
    log = logging.getLogger('')
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    setup(app)

    app['tc_prefix'] = os.environ['TC_PREFIX']
    app['secret'] = os.environ['PLATRON_SECRET']
    app['check_url'] = os.environ['CHECK_URL']
    app['t_db'] = dict()
    app['check'] = Queue()
    app['result'] = Queue()
    app['log'] = log

    app.on_startup.append(start_bg_tasks)
    app.on_cleanup.append(cleanup_bg_tasks)

    return app
