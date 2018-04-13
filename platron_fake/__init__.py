import asyncio
import os
from queue import Queue

from aiohttp import web
from platron_fake.hooks import process_check
from platron_fake.routes import setup


async def check_task(app: web.Application):
    try:
        await asyncio.sleep(0.01)
        while True:
            print(f'background task is working')
            if not app['check'].empty():
                print('PROCESS CHECK RUNNING')
                await process_check(app, app['ipn'].get())
            await asyncio.sleep(1.5)
    except asyncio.CancelledError:
        print('Cancel ipn listener..')


async def start_bg_tasks(app: web.Application):
    app['check_task_'] = app.loop.create_task(check_task(app))


async def cleanup_bg_tasks(app: web.Application):
    print('cleanup background tasks')
    app['check_task_'].cancel()


def create_app() -> web.Application:
    app = web.Application()
    setup(app)

    app['tc_prefix'] = os.environ['TC_PREFIX']
    app['secret'] = os.environ['PLATRON_SECRET']
    app['check_url'] = os.environ['CHECK_URL']
    app['t_db'] = dict()
    app['check'] = Queue()

    app.on_startup.append(start_bg_tasks)
    app.on_cleanup.append(cleanup_bg_tasks)

    return app
