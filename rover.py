import socket
import time
import random
from threading import Thread
from protocol import RoverMessage, PORTS

class LunarRover:
    def __init__(self):
        self.sensors = {
            'temperature': -50,
            'radiation': 120,
            'altitude': 100,
            'battery': 100
        }
        self.seq_nums = {sensor: 0 for sensor in self.sensors}
        self.running = True
        self.socks = {
            sensor: socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for sensor in self.sensors
        }
        self.command_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _update_sensors(self):
        self.sensors.update({
            'temperature': -50 + random.randint(-5, 5),
            'radiation': 120 + random.randint(-10, 10),
            'battery': max(0, self.sensors['battery'] - 0.1)
        })

    def _send_sensor_data(self, sensor_type):
        while self.running:
            self.seq_nums[sensor_type] += 1
            msg = RoverMessage(
                msg_type=sensor_type,
                seq_num=self.seq_nums[sensor_type],
                payload=self.sensors[sensor_type]
            )
            port_config = PORTS[sensor_type]
            self.socks[sensor_type].sendto(
                msg.serialize(),
                (port_config[1], port_config[2])
            print(f"📤 {sensor_type} sent")
            intervals = {
            'temperature': 5,   # Every 5 seconds
            'radiation': 5,     
            'altitude': 5,
            'battery': 10       # Every 10 seconds
            }
            time.sleep(intervals[sensor_type])  # ⚠️ Slow down transmissions

    def command_handler(self):
        self.command_sock.bind(('', PORTS['command'][0]))
        print(f"🎧 Command listener on {PORTS['command'][0]}")
        
        while self.running:
            try:
                data, addr = self.command_sock.recvfrom(1024)
                msg = RoverMessage.deserialize(data)
                print(f"📥 Command: {msg.payload}")
            except Exception as e:
                print(f"⚠️ Command error: {str(e)}")

    def start(self):
        self._update_sensors()
        for sensor in self.sensors:
            Thread(target=self._send_sensor_data, args=(sensor,)).start()
        Thread(target=self.command_handler).start()
        print("🤖 Rover operational!")

if __name__ == "__main__":
    LunarRover().start()
