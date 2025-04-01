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
        """Handles one communication channel with its own socket"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', listen_port))
        print(f"🌐 Channel opened on port {listen_port} → {dest_ip}:{dest_port}")
        
        try:
            while self.running:
                data, addr = sock.recvfrom(1024)
                self.bw_limiter.acquire(len(data))
                
                if self._simulate_loss():
                    print(f"🔥 Packet lost on port {listen_port}")
                    continue
                    
                Thread(
                    target=self._delayed_forward,
                    args=(data, (dest_ip, dest_port))
                ).start()
        finally:
            sock.close()
    
    def _delayed_forward(self, data, dest_addr):
        """Forwards data after applying space delays"""
        self._simulate_delay()
        # Create temporary forwarding socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as fwd_sock:
            fwd_sock.sendto(data, dest_addr)
        print(f"🚀 Forwarded {len(data)} bytes to {dest_addr}")
    
    def start(self):
        """Launches all communication channels"""
        threads = []
        for name, (listen_port, dest_ip, dest_port) in PORTS.items():
            t = Thread(
                target=self.proxy_handler,
                args=(listen_port, dest_ip, dest_port),
                daemon=True
            )
            t.start()
            threads.append(t)
            print(f"🛰️ {name.upper()} channel started")
        
        try:
            while True:  # Keep main thread alive
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down channels...")
            self.running = False
            for t in threads:
                t.join(timeout=1)

if __name__ == "__main__":
    ChannelSimulator().start()
