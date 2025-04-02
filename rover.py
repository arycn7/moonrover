import socket
import time
import random
from threading import Thread
from protocol import RoverMessage, PORTS

class LunarRover:
    def __init__(self):
        """
        Initializes the LunarRover instance with sensor data, sequence numbers,
        sockets for communication, and a command socket for receiving commands.
        """
        # Initial sensor readings
        self.sensors = {
            'temperature': -50,  # Initial temperature in degrees Celsius
            'radiation': 120,    # Initial radiation level in arbitrary units
            'altitude': 100,     # Initial altitude in meters
            'battery': 100       # Initial battery level as a percentage
        }
        # Sequence numbers for each sensor's data packets
        self.seq_nums = {sensor: 0 for sensor in self.sensors}
        # Flag to control the rover's operation
        self.running = True
        # Sockets for sending sensor data
        self.socks = {
            sensor: socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for sensor in self.sensors
        }
        # Socket for receiving commands
        self.command_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _update_sensors(self):
        """
        Updates the sensor readings with simulated random values.
        """
        self.sensors.update({
            'temperature': -50 + random.randint(-5, 5),  # Random fluctuation in temperature
            'radiation': 120 + random.randint(-10, 10),  # Random fluctuation in radiation
            'battery': max(0, self.sensors['battery'] - 0.1)  # Gradual battery drain
        })

    def _send_sensor_data(self, sensor_type):
        """
        Sends sensor data for a specific sensor type at regular intervals.
        Args:
            sensor_type (str): The type of sensor (e.g., 'temperature', 'radiation').
        """
        while self.running:
            # Define transmission intervals for each sensor type
            intervals = {
                'temperature': 5,  # Send every 5 seconds
                'radiation': 5,    # Send every 5 seconds
                'altitude': 5,     # Send every 5 seconds
                'battery': 5       # Send every 5 seconds
            }
            # Pause before sending the next data packet
            time.sleep(intervals[sensor_type])
            # Increment the sequence number for the sensor
            self.seq_nums[sensor_type] += 1
            # Create a RoverMessage with the sensor data
            msg = RoverMessage(
                msg_type=sensor_type,
                seq_num=self.seq_nums[sensor_type],
                payload=self.sensors[sensor_type]
            )
            # Retrieve the port configuration for the sensor
            port_config = PORTS[sensor_type]
            # Send the serialized message to the specified address and port
            self.socks[sensor_type].sendto(
                msg.serialize(),
                (port_config[1], port_config[2])
            )
            print(f"📤 {sensor_type} sent")  # Log the transmission  

    def command_handler(self):
        """
        Listens for and processes incoming commands from the command socket.
        """
        # Bind the command socket to the specified port
        self.command_sock.bind(('', PORTS['command'][0]))
        print(f"🎧 Command listener on {PORTS['command'][0]}")  # Log the listener status
        
        while self.running:
            try:
                # Receive data from the command socket
                data, addr = self.command_sock.recvfrom(1024)
                # Deserialize the received data into a RoverMessage
                msg = RoverMessage.deserialize(data)
                print(f"📥 Command: {msg.payload}")  # Log the received command
            except Exception as e:
                # Log any errors that occur while processing commands
                print(f"⚠️ Command error: {str(e)}")

    def start(self):
        """
        Starts the rover's operations, including sensor updates, data transmission,
        and command handling.
        """
        # Perform an initial update of the sensor readings
        self._update_sensors()
        # Start a thread for each sensor to send its data
        for sensor in self.sensors:
            Thread(target=self._send_sensor_data, args=(sensor,)).start()
        # Start a thread to handle incoming commands
        Thread(target=self.command_handler).start()
        print("🤖 Rover operational!")  # Log the rover's operational status

if __name__ == "__main__":
    # Create and start the LunarRover instance
    LunarRover().start()
