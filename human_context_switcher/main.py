#!/usr/bin/env python3
from . import console
from . import config

def main():
    try:
        c = console.Console.load(config.Config['db_path'])
        c.run()
    except KeyboardInterrupt:
        pass
    finally:
        c.dump()

if __name__ == '__main__':
    main()
