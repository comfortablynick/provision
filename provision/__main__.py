import logging

from .cli import main

logging.basicConfig(format="%(levelname)s:%(funcName)s: %(message)s")
LOG = logging.getLogger(__name__)

if __name__ == "__main__":
    main()
