
import json
from dataclasses import dataclass

# SET THESE TO YOUR ACTUAL LAPTOP IPs (from ipconfig/ifconfig)
EARTH_IP = "10.179.66.119"  # Earth station laptop IP
ROVER_IP = "10.179.66.156"   # Rover laptop IP

PORTS = {
    'telemetry': (50000, EARTH_IP, 50000),  # (listen_port, dest_ip, dest_port)
    'command': (50001, ROVER_IP, 50001),
    'science': (50002, EARTH_IP, 50002),
    'status': (50003, EARTH_IP, 50003)
}

MOON_DELAY = (1.28, 2.56)  # Light delay in seconds
PACKET_LOSS_PROB = 0.3       # 30% packet loss
MAX_BANDWIDTH = 1024        # 1KB/s per channel

@dataclass
class RoverMessage:
    msg_type: str
    seq_num: int
    payload: dict
    checksum: int = 0

    def serialize(self):
        # Calculate checksum BEFORE including it
        temp_data = {
            "msg_type": self.msg_type,
            "seq_num": self.seq_num,
            "payload": self.payload
        }
        data_bytes = json.dumps(temp_data).encode()
        self.checksum = sum(data_bytes) % 256
        
        # Now include checksum
        final_data = temp_data.copy()
        final_data["checksum"] = self.checksum
        return json.dumps(final_data).encode()

    @classmethod
    def deserialize(cls, data):
        msg_dict = json.loads(data.decode())
        
        # Validate checksum
        received_checksum = msg_dict.get("checksum", 0)
        calc_data = {
            "msg_type": msg_dict["msg_type"],
            "seq_num": msg_dict["seq_num"],
            "payload": msg_dict["payload"]
        }
        calc_bytes = json.dumps(calc_data).encode()
        calc_checksum = sum(calc_bytes) % 256
        
        if calc_checksum != received_checksum:
            raise ValueError(f"Checksum mismatch (sent {received_checksum} vs calc {calc_checksum})")
            
        return cls(**msg_dict)
