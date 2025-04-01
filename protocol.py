import json
from dataclasses import dataclass

# SET THESE TO ACTUAL LAPTOP IPs FROM HOTSPOT CONNECTION
EARTH_IP = "10.179.66.119"  # Earth station laptop IP
ROVER_IP = "10.179.66.156"   # Rover laptop IP

# Communication Ports (bi-directional channels)
PORTS = {
    'telemetry': (50000, EARTH_IP, 50000),  # (listen_port, dest_ip, dest_port)
    'command': (50001, ROVER_IP, 50001),
    'science': (50002, EARTH_IP, 50002),
    'status': (50003, EARTH_IP, 50003),
    'video': (50004, EARTH_IP, 50004)
}

# Moon-Earth Channel Characteristics
MOON_DELAY = (1.28, 2.56)  # 1.28-2.56 second delay
PACKET_LOSS_PROB = 0.3       # 30% packet loss
MAX_BANDWIDTH = 1024        # 1KB/s per channel

@dataclass
class RoverMessage:
    msg_type: str
    seq_num: int
    payload: dict
    checksum: int = 0

    def serialize(self):
        data = json.dumps(self.__dict__).encode()
        self.checksum = sum(data) % 256  # Simple checksum
        return json.dumps(self.__dict__).encode()

    @classmethod
    def deserialize(cls, data):
        msg = json.loads(data.decode())
        if sum(data) % 256 != msg['checksum']:
            raise ValueError("Checksum mismatch")
        return cls(**msg)
