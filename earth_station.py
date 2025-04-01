import socket
from threading import Thread
from protocol import PORTS, RoverMessage

class EarthStation:
    def __init__(self):
        self.socks = {
            sensor: socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for sensor in ['temperature', 'radiation', 'altitude', 'battery']
        }
        self.command_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _sensor_listener(self, sensor_type):
        sock = self.socks[sensor_type]
        port = PORTS[sensor_type][0]
        sock.bind(('0.0.0.0', port))
        print(f"👂 {sensor_type} on {port}")
        
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                msg = RoverMessage.deserialize(data)
                print(f"🌍 {sensor_type}: {msg.payload} (seq: {msg.seq_num})")
            except Exception as e:
                print(f"⚠️ {sensor_type} error: {str(e)}")

    def send_command(self, command):
        msg = RoverMessage(
            msg_type='command',
            seq_num=1,  # Implement sequence management
            payload=command
        )
        self.command_sock.sendto(
            msg.serialize(),
            (PORTS['command'][1], PORTS['command'][2]))
        print(f"📡 Sent command: {command}")

    def start(self):
        for sensor in self.socks:
            Thread(target=self._sensor_listener, args=(sensor,)).start()
        print("🛰️ Earth station online")

if __name__ == "__main__":
    import time
    station = EarthStation()
    station.start()
    
    time.sleep(5)
    station.send_command("MOVE NORTH 10m")
    
    while True: time.sleep(1)
