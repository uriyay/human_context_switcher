I want to supply a console for storing mind context.
The idea is to be able to make a context switch without loss of data.
There will be a couple of threads.

The thread
-------------

Each thread has:
1. A stack - thats extremely useful for go back from one thought that was spreaded from another.
2. A memory - not like computers, threads will have a memory which will make the whole thing of storing data and pull it very convenient.
3. An event loop - for sending events from one thread to other. You can send message to the main thread, like "go to launch" at specific time.
    Or you can send a more soficticated event for documentation, like "this command returns these results".

The memory
------------
A key-value memory

Example session
----------------
Here is an example for how this is work:
```
> push Idea1
> push Idea2
> push Idea3
> info stack
-------
|Idea3|
|Idea2|
|Idea1|
-------
> pop
> info stack
-------
|Idea2|
|Idea1|
-------
```

run "help" in order to see the whole list of commands:
```
main> help
Available commands are:
help: Shows help
new:
        Creates a new thread.
        param name: the name of the thread. you can pass nothing
            and a special name will be generated for you

switch:
        Switches to other thread.
        param name: the thread name

delete:
        Deletes thread.
        param name: the thread name

list:
        Get a list of all threads, also will mark the current thread by "[+]"

push:
        Pushes data to the stack

pop:
        Pops the last element that was inserted to the stack

set:
        Sets a key in memory to the given value.
        Syntax: "<key>" : "<value>"

get:
        Gets a value that was stored in a given key.
        param key: the key that was related to the data

info:
        Get info about the thread.
        available subcommands:
            info stack - displays the thread stack
            info memory - displays the thread memory

exit: Exits the console
shell:
        Will run the rest of the line as shell command

py:
        Will run IPython shell

remind:
        Search a phrase.
        param phrase: a phrase to search

#:
        A comment, will not be executed

google:
        Search a phrase in google.
        param phrase: a phrase to search in google

Also you can type a text wrapped by "`" in order to run to run it with python.
for example: "push `1+1`" will push 2).
In a similar way you can wrap a text by "$" in order to run it with the command line.
main>
```

Future thoughts
----------------
I want to combine it with my tags-db project, an automated tagging
So when the user will type: "remind <text>"
He will get a related memory, then a raw_input('phrase: ') to catch a phrase

Issues
-------
1. There was a weird problem with pip.
When installing a package it says:
```
File "/home/user/anaconda3/lib/python3.6/site-packages/pip/_vendor/pkg_resources/__init__.py", line 2121, in _rebuild_mod_path
    orig_path.sort(key=position_in_sys_path)
AttributeError: '_NamespacePath' object has no attribute 'sort'
```
I solved it by edit the line to:
```
orig_path._path.sort(key=position_in_sys_path)
```
2. If you can't see other languages than english in linux, run this command before running the main.py:
```
export LANG=en_US.UTF-8
```
and open main.py in new bash
