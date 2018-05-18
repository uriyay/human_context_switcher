#!/usr/bin/env python3
import time
import threading

from . import console
from . import config
from . import event_loop

class App(object):
    def __init__(self):
        self.event_loop = event_loop.EventLoop()
        self.console = console.Console.load(config.Config['db_path'], event_loop=self.event_loop)
        self.event_loop_thread = None

    def main(self):
        self.event_loop_thread = threading.Thread(target=self.event_loop.main_loop)

        #run
        self.event_loop_thread.start()
        self.console.run()

        #shutdown
        self.console.dump()
        self.event_loop.shutdown()
        if self.event_loop_thread is not None:
            self.event_loop_thread.join()

if __name__ == '__main__':
    App().main()
