import socket
from threading import Thread
from protocol import PORTS, EARTH_IP, RoverMessage

class EarthStation:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence = 0
        
    def send_command(self, command):
        self.sequence += 1
        msg = RoverMessage(
            msg_type='command',
            seq_num=self.sequence,
            payload=command
        )
        dest = (PORTS['command'][1], PORTS['command'][2])
        self.sock.sendto(msg.serialize(), dest)
        print(f"📡 Sent command: {command}")

    def telemetry_listener(self):
        self.sock.bind((EARTH_IP, PORTS['telemetry'][0]))
        
        while True:
            data, addr = self.sock.recvfrom(1024)
            try:
                msg = RoverMessage.deserialize(data)
                print(f"🌍 Telemetry Update:")
                for k, v in msg.payload.items():
                    print(f"  {k:>10}: {v}")
                print()
            except ValueError:
                print("⚠️ Corrupted telemetry packet")

    def start(self):
        Thread(target=self.telemetry_listener).start()
        print("🛰️ Earth station online")

if __name__ == "__main__":
    import time
    station = EarthStation()
    station.start()
    
    # Demo command after 10 seconds
    time.sleep(10)
    station.send_command({
        'action': 'move',
        'direction': 'north',
        'distance': 10
    })