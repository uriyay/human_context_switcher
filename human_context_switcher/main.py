#!/usr/bin/env python3
import asyncio
import time

from . import console
from . import config
from . import event_loop

class App(object):
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.event_loop = event_loop.EventLoop(self.loop)
        self.console = console.Console.load(config.Config['db_path'])

    @asyncio.coroutine
    def run_console(self):
        self.console.run()
        self.event_loop.shutdown()

    @asyncio.coroutine
    def close_loop(*args):
        loop.stop()
        loop.close()

    def main(self):
        try:
            self.loop.run_until_complete(
                asyncio.gather(self.event_loop.main_loop(),
                    self.run_console()))
        finally:
            self.console.dump()
            self.event_loop.shutdown()

        self.close_loop()

if __name__ == '__main__':
    App().main()
