from multiprocessing import Process, Queue

import logging
import logging.handlers

class LogListener(Process):
    """Listener class that handles logging info for the worker processes"""

    def __init__(self, listen_queue: Queue, logfile_name: str):
        super().__init__(daemon=True)
        self.listen_queue = listen_queue
        self.logfile_name = logfile_name

    def run(self):
        # Set up logfile
        root = logging.getLogger()
        h = logging.handlers.RotatingFileHandler(self.logfile_name, "a")
        f = logging.Formatter(
            "%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s"
        )
        h.setFormatter(f)
        root.addHandler(h)
        while True:
            next_message = self.listen_queue.get()
            if next_message is None:
                break
            logger = logging.getLogger(next_message.name)
            logger.handle(next_message)