import socket
import time
import random
from threading import Thread
from protocol import RoverMessage, PORTS

class LunarRover:
    def __init__(self):
        # Separate sockets for sending/receiving
        self.telemetry_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.command_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.seq_num = 0
        self.running = True
        self.position = (0, 0)
        
        self.sensors = {
            'temp': -50,
            'radiation': 120,
            'altitude': 100,
            'battery': 100,
            'position': self.position
        }

    def _update_sensors(self):
        self.sensors.update({
            'temp': -50 + random.randint(-5, 5),
            'radiation': 120 + random.randint(-10, 10),
            'battery': max(0, self.sensors['battery'] - 0.1),
            'position': self.position
        })

    def _generate_telemetry(self):
        while self.running:
            self.seq_num += 1
            self._update_sensors()
            msg = RoverMessage(
                msg_type='telemetry',
                seq_num=self.seq_num,
                payload=self.sensors
            )
            # Send to Earth's IP:PORT from protocol.py
            self.telemetry_sock.sendto(
                msg.serialize(),
                (PORTS['telemetry'][1], PORTS['telemetry'][2])
            )
            print(f"📤 Sent telemetry #{self.seq_num}")
            time.sleep(5)

    def command_handler(self):
        # Bind to ALL interfaces on command port
        self.command_sock.bind(('', PORTS['command'][0]))
        print(f"🎧 Listening for commands on port {PORTS['command'][0]}")
        
        while self.running:
            try:
                data, addr = self.command_sock.recvfrom(1024)
                msg = RoverMessage.deserialize(data)
                print(f"📥 Received command: {msg.payload}")
                # Execute command logic here
            except Exception as e:
                print(f"⚠️ Command error: {str(e)}")

    def start(self):
        Thread(target=self._generate_telemetry).start()
        Thread(target=self.command_handler).start()
        print("🤖 Rover operational!")

if __name__ == "__main__":
    LunarRover().start()
