#!/usr/bin/env python
import console
import config

if __name__ == '__main__':
    try:
        c = console.Console.load(config.Config['db_path'])
        c.run()
    finally:
        c.dump()
