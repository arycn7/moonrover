import time

class BandwidthLimiter:
    def __init__(self, max_bps):
        self.max_bps = max_bps
        self.start_time = time.time()
        self.bytes_sent = 0

    def acquire(self, data_size):
        while True:
            elapsed = time.time() - self.start_time
            if elapsed == 0:
                return
            current_bps = self.bytes_sent / elapsed
            if current_bps < self.max_bps:
                self.bytes_sent += data_size
                return
            time.sleep(0.1)
