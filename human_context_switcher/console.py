import IPython
import json
import sys
import os
import readline
import subprocess
from google import google
import colored
import urllib

from . import thread
from . import config
from . import msdn
from . import man

if sys.version_info.major == 2:
    raise Exception('Python 2 is not supported')

RESET = colored.attr('reset')
WIKI_URL = 'http://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles={0}'
WIKI_SEARCH_URL = 'http://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={0}'

readline.parse_and_bind('tab: complete')

class Console(object):
    def __init__(self, is_load_mode=False):
        if not is_load_mode:
            self.main_thread = thread.Thread(name='main')
            self.threads = {'main' : self.main_thread}
            self.current_thread = self.main_thread
        self.should_stop = False
        self.commands = {
            'help' : self.help,
            'new' : self.new_thread,
            'switch' : self.switch,
            'delete' : self.delete_command,
            'list' : self.list_threads,
            'push' : self.push,
            'pop' : self.pop,
            'set' : self.set_data,
            'get' : self.get_data,
            'info' : self.info,
            'exit' : self.exit,
            'shell' : self.run_shell,
            'py' : self.run_python,
            'remind' : self.remind,
            '#' : self.comment,
            'google' : self.google,
            'wiki' : self.wikipedia,
            'msdn' : self.get_msdn,
            'man': self.get_man_page,
        }

    def help(self, line):
        '''Shows help'''
        print('Available commands are:\n{}'.format(
            '\n'.join('{0}{1}{2}: {3}'.format(
                colored.fg('yellow'), func_name, RESET, func.__doc__)
                for func_name,func in self.commands.items())
            ))
        print('\n'.join(['Also you can type a text wrapped by "`" in order to run to run it with python.',
                'for example: "push `1+1`" will push 2).',
                'In a similar way you can wrap a text by "$" in order to run it with the command line.']))

    def comment(self, line):
        '''
        A comment, will not be executed
        '''
        pass

    def google(self, line):
        '''
        Search a phrase in google.
        syntax: google [push|set] phrase
        param push: push the first result to the stack
        param set: set the phrase in memory to the first result
        param phrase: a phrase to search in google
        '''
        param,rest_line = line.partition(' ')[0::2]
        if param in ['push', 'set']:
            line = rest_line
        results = [(x.description, x.link) for x in google.search(line)]
        first_result = '{0}\n{1}'.format(results[0][0], results[0][1])
        if param == 'push':
            print('Pushing first_result:\n' + first_result)
            self.push(first_result)
        elif param == 'set':
            print('memory["{0}"] = "{1}"'.format(line, first_result))
            self.current_thread.set_data(line, first_result)
        else:
            for index,result in enumerate(results):
                print('{0}[result #{1}]{2}\n{3}\n{4}\n'.format(colored.fg('yellow'), index, RESET, result[0], result[1]))

    def wikipedia(self, line):
        '''
        Gets wikipedia info about something
        Syntax: wiki [push|set] phrase
        '''
        param,rest_line = line.partition(' ')[0::2]
        if param in ['push', 'set']:
            line = rest_line
        #first find a match term for this phrase in wikipedia
        search_results = json.loads(urllib.request.urlopen(WIKI_SEARCH_URL.format(urllib.request.quote(line))).read())
        search_results = [x['title'] for x in search_results['query']['search']]
        if len(search_results) == 0:
            print('Nothing found..')
        else:
            print('Found these possible values:\n' + '\n'.join(
                '{0}) {1}'.format(i, val) for i,val in enumerate(search_results)))
            chosen = int(input('Choose a value ({0}-{1}): '.format(0, len(search_results))))
            title = search_results[chosen]
            wiki_value = json.loads(urllib.request.urlopen(WIKI_URL.format(urllib.request.quote(title))).read())
            wiki_value_pages = wiki_value['query']['pages']
            intro = wiki_value_pages[list(wiki_value_pages.keys())[0]]['extract']
            print(intro)
            if param == 'push':
                self.push(intro)
            elif param == 'set':
                self.current_thread.set_data(line, intro)

    def get_msdn(self, line):
        '''
        Gets msdn about function
        param function_name: the function to get msdn about
        '''
        m = msdn.MSDN(line)
        print('Syntax:\n{0}\nParameters:\n{1}\nReturn value:\n{2}'.format(m.syntax, m.parameters, m.return_value))

    def get_man_page(self, line):
        '''
        Gets man page
        syntax: man <topic> [section]
        '''
        section = None
        topic = line
        if ' ' in line:
            topic, section = line.split(' ')
        print(man.get_man_page(topic, section))

    def exit(self, line):
        '''Exits the console'''
        self.should_stop = True

    def new_thread(self, line):
        '''
        Creates a new thread.
        param name: the name of the thread. you can pass nothing
            and a special name will be generated for you
        '''
        name = line
        if len(line) == 0:
            name = None
        t = thread.Thread(name)
        self.threads[t.thread_name] = t
        self.current_thread = t

    def switch(self, line):
        '''
        Switches to other thread.
        param name: the thread name
        '''
        if len(line) == 0:
            line = 'main'
        self.current_thread = self.threads[line]

    def delete_command(self, line):
        '''
        Delete command.
        syntax: delete thread|memory
        param name: the thread name or key name
        '''
        param, line = line.partition(' ')[0::2]
        if param == 'thread':
            if len(line) == 0:
                line = self.current_thread.thread_name
            if input('Are you sure you want to delete "{0}" thread? (Y/n): '.format(line)).lower() == 'y':
                if line not in self.threads:
                    print('thread "{0}" not found'.format(line))
                else:
                    del self.threads[line]
                    #switch to main thread
                    self.switch('')
        elif param == 'memory':
            if len(line) == 0:
                print('Error: no key name given to delete')
            else:
                if input('Are you sure you want to delete "{0}" key from memory? (Y/n): '.format(line)).lower() == 'y':
                    if line not in self.current_thread.memory:
                        print('memory key "{0}" not found'.format(line))
                    else:
                        del self.current_thread.memory[line]

    def list_threads(self, line):
        '''
        Get a list of all threads, also will mark the current thread by "[+]"
        '''
        def display_thread(t):
            mark = {True : '+', False : '-'}[self.current_thread is t]
            return '[{0}] {1}'.format(mark, t.thread_name)

        print('Threads:\n' + '\n'.join(display_thread(t) for t in self.threads.values()))

    def info(self, line):
        '''
        Get info about the thread.
        available subcommands:
            info stack - displays the thread stack
            info memory - displays the thread memory
        '''
        line = line.strip()
        if line == 'stack':
            print(self.current_thread.display_stack())
        elif line == 'memory':
            print(self.current_thread.display_memory())
        else:
            print('Invalid command')

    def run_shell(self, line):
        '''
        Will run the rest of the line as shell command
        '''
        os.system(line)

    def run_python(self, line):
        '''
        Will run IPython shell
        '''
        IPython.embed()

    def push(self, line):
        '''
        Pushes data to the stack
        '''
        self.current_thread.push(line)

    def pop(self, line):
        '''
        Pops the last element that was inserted to the stack
        '''
        data = self.current_thread.pop()
        print(repr(data))

    def set_data(self, line):
        '''
        Sets a key in memory to the given value.
        Syntax: "<key>" : "<value>"
        '''
        parts = line.split('"')
        #0"1"2:"3"4
        assert ':' in parts[2]
        key, value = parts[1], parts[3]
        self.current_thread.set_data(key, value)

    def get_data(self, line):
        '''
        Gets a value that was stored in a given key.
        param key: the key that was related to the data
        '''
        print(repr(self.current_thread.get_data(line)))

    def remind(self, line):
        '''
        Search a phrase.
        param phrase: a phrase to search
        '''
        #stop condition
        if line == '':
            return

        new_phrase = ''
        for name,thd in self.threads.items():
            print('In thread {}'.format(name))
            new_phrase += thd.remind(line)

        if new_phrase == '':
            new_phrase = input('Next phrase?: ')
        self.remind(new_phrase)


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
            line = input('{0}{1}{2}> '.format(colored.fg('red'), self.current_thread.thread_name, RESET))
            if len(line) > 0:
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
