import socket
import time
import json
from threading import Thread
from protocol import RoverMessage, PORTS, ROVER_IP

class LunarRover:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
            'battery': max(0, self.sensors['battery'] - 0.1)
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
            self._send_message(msg, PORTS['telemetry'][1:])
            time.sleep(5)
            
    def _send_message(self, msg, dest):
        self.sock.sendto(msg.serialize(), dest)
            
    def command_handler(self):
        self.sock.bind((ROVER_IP, PORTS['command'][0]))
        
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                msg = RoverMessage.deserialize(data)
                
                if msg.msg_type == 'command':
                    response = self._execute_command(msg.payload)
                    self._send_ack(msg.seq_num)
            except ValueError as e:
                print(f"Invalid command: {e}")

    def _execute_command(self, command):
        action = command.get('action')
        if action == 'move':
            distance = command.get('distance', 0)
            direction = command.get('direction', 'north')
            # Simplified movement logic
            x, y = self.position
            if direction == 'north': y += distance
            elif direction == 'south': y -= distance
            elif direction == 'east': x += distance
            elif direction == 'west': x -= distance
            self.position = (x, y)
            return {'status': 'OK', 'new_position': self.position}
        return {'status': 'ERROR', 'reason': 'Unknown command'}

    def start(self):
        Thread(target=self._generate_telemetry).start()
        Thread(target=self.command_handler).start()
        print("🤖 Rover operational")

if __name__ == "__main__":
    LunarRover().start()