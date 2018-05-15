import asyncio
import time
import collections

class Event(object):
    def __init__(self, event_id, name, data=None):
        self.event_id = event_id
        self.name = name
        self.data = data
        self.time = time.time()

    def __str__(self):
        return '<Event id={0} name="{1}" data={2} time={3}>'.format(
                self.event_id, self.name, self.data, self.time)

class EventID:
    SHUTDOWN = 0

class ShutdownEvent(Event):
    def __init__(self):
        super(ShutdownEvent, self).__init__(EventID.SHUTDOWN, 'shutdown')

class EventLoop(object):
    def __init__(self, loop):
        self.loop = loop
        self.queue = asyncio.Queue(loop=self.loop)
        self.callbacks = collections.defaultdict(list)

    @asyncio.coroutine
    def main_loop(self):
        while True:
            event = yield from self.queue.get()
            print(event)
            if event.event_id == 0 and event.name == 'shutdown':
                print('exit main_loop')
                break
            else:
                for callback in self.callbacks[event.event_id]:
                    callback(event)

    def send_event(self, event):
        self.queue.put_nowait(event)

    def shutdown(self):
        self.queue.put_nowait(ShutdownEvent())

    def register_callback(self, event_id, callback):
        self.callbacks[event_id].append(callback)

    def unregister_callback(self, event_id, callback):
        if callback in self.callbacks[event_id]:
            self.callbacks[event_id].remove(callback)
