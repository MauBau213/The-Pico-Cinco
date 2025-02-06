import time

class Stopwatch:
    def __init__(self):
        self.started = False
        self.start_time = 0
        self.elapsed_time = 0

    def start(self):
        if not self.started:
            self.start_time = time.time()
            self.started = True
            print("Stopwatch started.")
        else:
            print("The stopwatch is already running.")

    def reset(self):
        self.started = False
        self.start_time = 0
        self.elapsed_time = 0
        print("Stopwatch reset.")

    def get_time(self):
        if self.started:
            self.elapsed_time = time.time() - self.start_time
            return self.elapsed_time
        else:
            print("The stopwatch is not running.")
            return 0

    def is_less_than(self, seconds):
        if self.started:
            elapsed_time = time.time() - self.start_time
            if elapsed_time < seconds:
                return True
            else:
                return False
        else:
            print("The stopwatch is not running.")
            return False