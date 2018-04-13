from aiohttp import web
import asyncio

from platron_fake import create_app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='localhost', port=6969)
