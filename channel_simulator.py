import socket
import time
import random
from threading import Thread
from protocol import PORTS, MOON_DELAY, PACKET_LOSS_PROB, MAX_BANDWIDTH
from utils import BandwidthLimiter

class ChannelSimulator:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True
        self.bw_limiter = BandwidthLimiter(MAX_BANDWIDTH)

    def _simulate_delay(self):
        time.sleep(random.uniform(*MOON_DELAY))
        
    def _simulate_loss(self):
        return random.random() < PACKET_LOSS_PROB
        
    def proxy_handler(self, listen_port, dest_ip, dest_port):
        self.sock.bind(('', listen_port))
        
        while self.running:
            data, addr = self.sock.recvfrom(1024)
            self.bw_limiter.acquire(len(data))
            
            if self._simulate_loss():
                print(f"🔥 Packet lost on port {listen_port}")
                continue
                
            Thread(target=self._delayed_forward,
                   args=(data, (dest_ip, dest_port))).start()
    
    def _delayed_forward(self, data, dest_addr):
        self._simulate_delay()
        self.sock.sendto(data, dest_addr)
        print(f"🌐 Forwarded {len(data)}b to {dest_addr}")
    
    def start(self):
        for name, (listen_port, dest_ip, dest_port) in PORTS.items():
            Thread(target=self.proxy_handler,
                   args=(listen_port, dest_ip, dest_port)).start()
            print(f"🚀 Channel {name} listening on {listen_port}")

if __name__ == "__main__":
    ChannelSimulator().start()