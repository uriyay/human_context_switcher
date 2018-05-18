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
    ALARM = 2

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

class AlarmEvent(Event):
    def __init__(self, source_thread_name, source_thread_id, target_thread_id, data, start_time):
        super(AlarmEvent, self).__init__(EventID.ALARM, 'alarm',
                source_thread_name=source_thread_name,
                source_thread_id=source_thread_id,
                target_thread_id=target_thread_id,
                data=data)
        self.start_time = start_time

class EventLoop(object):
    def __init__(self):
        self.queue = queue.Queue()
        self.callbacks = collections.defaultdict(list)

    def main_loop(self):
        while True:
            time.sleep(0.1)
            event = self.queue.get()
            if event.event_id == EventID.SHUTDOWN:
                break
            elif event.event_id == EventID.ALARM:
                current_time = time.time()
                if event.start_time > current_time:
                    #put alarm event after a normal event
                    self.queue.put_nowait(event)
                    continue

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
