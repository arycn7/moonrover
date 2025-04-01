import socket
import time
import random
from threading import Thread
from protocol import PORTS, MOON_DELAY, PACKET_LOSS_PROB, MAX_BANDWIDTH
from utils import BandwidthLimiter

class ChannelSimulator:
    def __init__(self):
        self.running = True
        self.bw_limiter = BandwidthLimiter(MAX_BANDWIDTH)
        
    def _simulate_delay(self):
        time.sleep(random.uniform(*MOON_DELAY))
        
    def _simulate_loss(self):
        return random.random() < PACKET_LOSS_PROB
        
    def proxy_handler(self, listen_port, dest_ip, dest_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', listen_port))
        print(f"🌐 Channel {listen_port}→{dest_port} open")
        
        try:
            while self.running:
                data, addr = sock.recvfrom(1024)
                self.bw_limiter.acquire(len(data))
                
                if self._simulate_loss():
                    print(f"🔥 Lost {len(data)}b on {listen_port}")
                    continue
                    
                Thread(
                    target=self._delayed_forward,
                    args=(data, (dest_ip, dest_port))
                ).start()
        finally:
            sock.close()
    
    def _delayed_forward(self, data, dest_addr):
        self._simulate_delay()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as fwd_sock:
            fwd_sock.sendto(data, dest_addr)
        print(f"🚀 Forwarded {len(data)}b to {dest_addr}")
    
    def start(self):
        for name, (listen_port, dest_ip, dest_port) in PORTS.items():
            Thread(
                target=self.proxy_handler,
                args=(listen_port, dest_ip, dest_port),
                daemon=True
            ).start()
        
        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Channel simulator shutting down")
            self.running = False

if __name__ == "__main__":
    ChannelSimulator().start()
