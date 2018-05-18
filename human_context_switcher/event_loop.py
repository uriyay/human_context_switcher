import time
import collections
import queue

class Event(object):
    def __init__(self,
            event_id,
            name,
            source_thread_name=None,
            source_thread_id=None,
            target_thread_id=None,
            data=None):
        self.event_id = event_id
        self.name = name
        self.data = data
        self.source_thread_name = source_thread_name
        self.source_thread_id = source_thread_id
        self.target_thread_id = target_thread_id
        self.time = time.time()

    def __str__(self):
        return '<Event id={0} name="{1}" data={2} time={3} from:{4} to:{5}>'.format(
                self.event_id, self.name, self.data, self.time,
                self.source_thread_id, self.target_thread_id)

class EventID:
    SHUTDOWN = 0
    MESSAGE = 1

class ShutdownEvent(Event):
    def __init__(self):
        super(ShutdownEvent, self).__init__(EventID.SHUTDOWN, 'shutdown')

class MessageEvent(Event):
    def __init__(self, source_thread_name, source_thread_id, target_thread_id, data):
        super(MessageEvent, self).__init__(EventID.MESSAGE, 'message',
                source_thread_name=source_thread_name,
                source_thread_id=source_thread_id,
                target_thread_id=target_thread_id,
                data=data)

class EventLoop(object):
    def __init__(self):
        self.queue = queue.Queue()
        self.callbacks = collections.defaultdict(list)

    def main_loop(self):
        while True:
            event = self.queue.get()
            if event.event_id == 0 and event.name == 'shutdown':
                break
            else:
                for thread_id, callback in self.callbacks[event.event_id]:
                    if event.target_thread_id == thread_id:
                        callback(event)

    def send_event(self, event):
        self.queue.put_nowait(event)

    def shutdown(self):
        self.queue.put_nowait(ShutdownEvent())

    def register_callback(self, event_id, thread_id, callback):
        self.callbacks[event_id].append((thread_id, callback))

    def unregister_callback(self, event_id, thread_id, callback):
        if callback in self.callbacks[event_id]:
            self.callbacks[event_id].remove((thread_id, callback))
