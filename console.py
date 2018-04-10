import IPython
import json
import sys
import os
import readline
import subprocess

import thread
import config

if sys.version_info.major == 2:
    raise Exception('Python 2 is not supported')

readline.parse_and_bind('tab: complete')

class Console(object):
    def __init__(self, is_load_mode=False):
        if not is_load_mode:
            self.main_thread = thread.Thread(name='main')
            self.threads = {'' : self.main_thread}
            self.current_thread = self.main_thread
        self.should_stop = False
        self.commands = {
            'new' : self.new_thread,
            'switch' : self.switch,
            'delete' : self.delete_thread,
            'list' : self.list_threads,
            'push' : self.push,
            'pop' : self.pop,
            'set' : self.set_data,
            'get' : self.get_data,
            'info' : self.info,
            'exit' : self.exit,
            'shell' : self.run_shell,
            'py' : self.run_python,
        }

    def exit(self, line):
        self.should_stop = True

    def new_thread(self, line):
        name = line
        if len(line) == 0:
            name = None
        t = thread.Thread(name)
        self.threads[t.thread_name] = t
        self.current_thread = t

    def switch(self, line):
        self.current_thread = self.threads[line]

    def delete_thread(self, line):
        del self.threads[line]

    def list_threads(self, line):
        def display_thread(t):
            mark = {True : '+', False : '-'}[self.current_thread is t]
            return '[{0}] {1}'.format(mark, t.thread_name)

        print('Threads:\n' + '\n'.join(display_thread(t) for t in self.threads.values()))

    def info(self, line):
        line = line.strip()
        if line == 'stack':
            print(self.current_thread.display_stack())
        elif line == 'memory':
            print(self.current_thread.display_memory())
        else:
            print('Invalid command')

    def run_shell(self, line):
        os.system(line)

    def run_python(self, line):
        IPython.embed()

    def push(self, line):
        self.current_thread.push(line)

    def pop(self, line):
        data = self.current_thread.pop()
        print(repr(data))

    def set_data(self, line):
        parts = line.split('"')
        #0"1"2,"3"4
        assert ',' in parts[2]
        key, value = parts[1], parts[3]
        self.current_thread.set_data(key, value)

    def get_data(self, line):
        print(repr(self.current_thread.get_data(line)))

    def parse(self, line):
        if '`' in line:
            parts = line.split('`')
            #replace all `code` with the result, in order to do this notice that every odd part is wrapped by "`"
            line = ''.join(str({True:eval, False:lambda y: y}[index%2 == 1](x)) for index,x in enumerate(parts))

        if '$' in line:
            def exec_shell(data):
                return subprocess.check_output(data, shell=True).decode('ascii')
            parts = line.split('$')
            #replace all $system command$ with the output, in order to do this notice that every odd part is wrapped by "$"
            line = ''.join(str({True:exec_shell, False:lambda y: y}[index%2 == 1](x)) for index,x in enumerate(parts))

        parts = line.partition(' ')
        if parts[0] not in self.commands:
            print('command "{}" is not defined'.format(parts[0]))
        else:
            handler = self.commands[parts[0]]
            handler(parts[2])

    def run(self):
        self.should_stop = False
        while not self.should_stop:
            line = input('{0}> '.format(self.current_thread.thread_name))
            self.parse(line)

    def dump(self):
        json.dump([self.main_thread.id, [x.dump() for x in self.threads.values()], self.current_thread.id],
                open(os.path.expanduser(config.Config['db_path']), 'w'))

    @classmethod
    def load(cls, path):
        path = os.path.expanduser(path)
        if os.path.exists(path):
            main_thread_id, threads_dumps, current_thread_id = json.load(open(path, 'r'))
            c = cls(is_load_mode=True)
            c.threads = {}
            for data in threads_dumps:
                t = thread.Thread.load(data)
                c.threads[t.thread_name] = t
            c.main_thread = next(x for x in c.threads.values() if x.id == main_thread_id)
            c.current_thread = next(x for x in c.threads.values() if x.id == current_thread_id)
            return c
        return cls()
