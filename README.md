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

run "help" in order to see the whole list of commands.

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
