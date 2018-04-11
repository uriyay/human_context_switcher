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

Future thoughts
----------------
I want to combine it with my tags-db project, an automated tagging
So when the user will type: "remind <text>"
He will get a related memory, then a raw_input('phrase: ') to catch a phrase

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

```
