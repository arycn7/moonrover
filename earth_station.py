import socket
import time
from threading import Thread
from protocol import PORTS, RoverMessage

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
        try:
            self.sock.sendto(
                msg.serialize(),
                (PORTS['command'][1], PORTS['command'][2])
            )
            print(f"📡 Sent command: {command}")
        except Exception as e:
            print(f"🚨 Command failed: {e}")

    def telemetry_listener(self):
        self.sock.bind(('0.0.0.0', PORTS['telemetry'][0]))
        print(f"👂 Listening on port {PORTS['telemetry'][0]}")
        
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                msg = RoverMessage.deserialize(data)
                print(f"🌍 Telemetry #{msg.seq_num}:")
                for k, v in msg.payload.items():
                    print(f"  {k:>10}: {v}")
                print()
            except ValueError as e:
                print(f"⚠️ Corruption: {str(e)}")
            except Exception as e:
                print(f"⚠️ General error: {str(e)}")

    def start(self):
        Thread(target=self.telemetry_listener, daemon=True).start()
        print("🛰️ Earth station online")

if __name__ == "__main__":
    station = EarthStation()
    station.start()
    
    # Send test command after 5 seconds
    time.sleep(5)
    station.send_command({
        'action': 'move',
        'direction': 'north',
        'distance': 10
    })
    
    # Keep program running
    while True: time.sleep(1)
