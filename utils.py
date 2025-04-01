import time
import random

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

def simulate_network_conditions():
    """Call this in channel_simulator to add variability"""
    global MOON_DELAY, PACKET_LOSS_PROB
    while True:
        MOON_DELAY = (
            random.uniform(1.0, 3.0),
            random.uniform(1.0, 3.0))
        PACKET_LOSS_PROB = random.uniform(0.2, 0.4)
        time.sleep(10)
