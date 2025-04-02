import json
from dataclasses import dataclass
import random
# IP Configuration
EARTH_IP = "10.179.66.119"  # Earth station laptop IP
ROVER_IP = "10.179.66.156"   # Rover laptop IP

# Separate Ports Configuration
PORTS = {
    'temperature': (51000, EARTH_IP, 51000),
    'radiation':    (51001, EARTH_IP, 51001),
    'altitude':     (51002, EARTH_IP, 51002),
    'battery':      (51003, EARTH_IP, 51003),
    'command':      (51004, ROVER_IP, 51004)
}

MOON_DELAY = (1.28, 2.56)
PACKET_LOSS_PROB = 0.05
MAX_BANDWIDTH = 1024

@dataclass
class RoverMessage:
    msg_type: str
    seq_num: int
    payload: float  # Single value now
    checksum: int = 0

    def serialize(self):
        temp_data = {
            "msg_type": self.msg_type,
            "seq_num": self.seq_num,
            "payload": self.payload
        }
        data_bytes = json.dumps(temp_data).encode()
        self.checksum = sum(data_bytes) % 256
        
        final_data = temp_data.copy()
        final_data["checksum"] = self.checksum
        return json.dumps(final_data).encode()

    @classmethod
    def deserialize(cls, data):
        msg_dict = json.loads(data.decode())
        
        # Validate checksum
        calc_data = {
            "msg_type": msg_dict["msg_type"],
            "seq_num": msg_dict["seq_num"],
            "payload": msg_dict["payload"]
        }
        calc_bytes = json.dumps(calc_data).encode()
        calc_checksum = sum(calc_bytes) % 256
        
        if calc_checksum != msg_dict["checksum"]:
            raise ValueError(f"Checksum mismatch {calc_checksum} vs {msg_dict['checksum']}")
            
        return cls(**msg_dict)
