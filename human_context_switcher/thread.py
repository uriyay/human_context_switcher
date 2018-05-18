import namesgenerator
import json
import string
from terminaltables import AsciiTable, SingleTable
import textwrap
import time

from .event_loop import EventID, MessageEvent, AlarmEvent

LINE_WIDTH = 80

class Thread(object):
    def __init__(self, console=None, event_loop=None, name=None, thread_id=None, stack=None, memory=None):
        self.id = id(self) if thread_id is None else thread_id
        self.thread_name = namesgenerator.get_random_name() if name is None else name
        self.stack = [] if stack is None else stack
        self.memory = {} if memory is None else memory
    
        self.console = console

        #main_loop
        self.event_loop = event_loop
        self.event_loop.register_callback(EventID.MESSAGE, self.id, self.recv)
        self.event_loop.register_callback(EventID.ALARM, self.id, self.recv)

    def __del__(self):
        self.event_loop.unregister_callback(EventID.MESSAGE, self.id, self.recv)

    def recv(self, event):
        if event.event_id == EventID.MESSAGE:
            print ('[Message] thread "%s" got "%s" from thread "%s"' % (
                self.thread_name, event.data, event.source_thread_name))
        elif event.event_id == EventID.ALARM:
            print('[Alarm] thread "%s" got alaram "%s" from thread "%s"' % (
                self.thread_name, event.data, event.source_thread_name))

        if event.data.startswith('cmd '):
            command = event.data.partition('cmd ')[-1].strip()

            current_thread = self.console.current_thread
            self.console.current_thread = self

            self.console.parse(command)

            self.console.current_thread = current_thread

    def send(self, target_thread_id, data):
        self.event_loop.send_event(MessageEvent(self.thread_name, self.id, target_thread_id, data))

    def set_alarm(self, data, miliseconds_offset):
        event_time = time.time() + (miliseconds_offset / 1000)
        self.event_loop.send_event(AlarmEvent(self.thread_name, self.id, self.id, data, event_time))

    def dump(self):
        return json.dumps([self.id, self.thread_name, self.stack, self.memory])

    @classmethod
    def load(cls, data, console=None, event_loop=None):
        thread_id, thread_name, stack, memory = json.loads(data)
        t = cls(console=console, event_loop=event_loop, name=thread_name, thread_id=thread_id, stack=stack, memory=memory)
        return t

    def push(self, data):
        self.stack.append(data)

    def pop(self):
        return self.stack.pop()

    def set_data(self, key, value):
        self.memory[key] = value

    def get_data(self, key):
        return self.memory[key]

    def _display_list(self, data_list):
        if len(data_list) == 0:
            return 'Nothing in here..'

        table = SingleTable([['\n'.join(textwrap.wrap(x, LINE_WIDTH))] for x in data_list])
        table.inner_row_border = True
        return table.table

    def display_stack(self):
        return self._display_list(self.stack[::-1])

    def display_memory(self):
        return self._display_list(['"{0}" : "{1}"'.format(key, value) for key,value in self.memory.items()])

    def _search(self, phrase, container):
        results = []
        for entry in container:
            #TODO: more soficiticated method
            if phrase.lower() in entry.lower():
                results.append(entry)
        return results

    def remind(self, phrase):
        print('in stack:')
        print(self._display_list(self._search(phrase, self.stack[::-1])))
        print('in memory:')
        print(self._display_list(self._search(phrase, self.memory.values())))
        #TODO: aggregate new tags from the results
        return ''
