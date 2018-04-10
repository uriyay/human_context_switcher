import namesgenerator
import json

class Thread(object):
    def __init__(self, name=None, thread_id=None, stack=None, memory=None):
        self.id = id(self) if thread_id is None else thread_id
        self.thread_name = namesgenerator.get_random_name() if name is None else name
        self.stack = [] if stack is None else stack
        self.memory = {} if memory is None else memory
        #TODO: an async event loop with timed events and callbacks for crazy things
        #self.event_loop = 

    def dump(self):
        return json.dumps([self.id, self.thread_name, self.stack, self.memory])

    @classmethod
    def load(cls, data):
        thread_id, thread_name, stack, memory = json.loads(data)
        t = cls(name=thread_name, thread_id=thread_id, stack=stack, memory=memory)
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

        max_data_length = max(len(x) for x in data_list)
        separator = '-' * (max_data_length + 2)
        result = '{0}\n{1}\n{0}'.format(separator,
                '\n'.join(('|{:^%d}|' % (max_data_length)).format(x) for x in data_list))
        return result

    def display_stack(self):
        return self._display_list(self.stack[::-1])

    def display_memory(self):
        return self._display_list(['"{0}" : "{1}"'.format(key, value) for key,value in self.memory.items()])
