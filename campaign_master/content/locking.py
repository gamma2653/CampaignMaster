import threading
import contextlib


# From my 2022 CUP Robotics work
# https://github.com/cornell-cup/c1c0-scheduler/blob/archive/grpc-impl/c1c0_scheduler/utils.py

class ReaderWriterSuite:
    """
    Standard Reader Writer
    """
    # Based on wikipedia:
    #   https://en.wikipedia.org/wiki/Readers%E2%80%93writer_lock

    g = threading.Lock()
    writer_active_con = threading.Condition(g)
    writer_active = False
    num_writers_waiting = 0
    num_readers_active = 0

    @contextlib.contextmanager
    def reader(self):
        self.acquire_reader()
        yield
        self.release_reader()

    @contextlib.contextmanager
    def writer(self):
        self.acquire_writer()
        yield
        self.release_writer()

    def acquire_reader(self):
        with self.g:
            while self.num_writers_waiting > 0 or self.writer_active:
                self.writer_active_con.wait()
            self.num_readers_active += 1

    def release_reader(self):
        with self.g:
            self.num_readers_active -= 1
            if self.num_readers_active == 0:
                self.writer_active_con.notify_all()

    def acquire_writer(self):
        with self.g:
            self.num_writers_waiting += 1
            while self.num_readers_active > 0 or self.writer_active:
                self.writer_active_con.wait()
            self.num_writers_waiting -= 1
            self.writer_active = True

    def release_writer(self):
        with self.g:
            self.writer_active = False
            self.writer_active_con.notify_all()