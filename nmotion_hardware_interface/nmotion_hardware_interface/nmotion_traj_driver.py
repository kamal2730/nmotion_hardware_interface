from nmotion_transport import *
import socket
import struct
import time
import math

HOST = "127.0.0.1"
PORT = 6006

# Socket server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)
print("Waiting for ROS FollowJointTrajectory client...")
conn, _ = sock.accept()
print("ROS connected")

# NMotion setup
iface = USBInterface("/dev/ttyACM0")
time.sleep(2)
act1 = Actuator(0, iface)
time.sleep(2)

try:
    while True:
        # receive: angle_rad (double) + speed_deg (double)
        data = conn.recv(16)
        if not data:
            break

        target_rad, speed = struct.unpack("dd", data)
        target_deg = math.degrees(target_rad)

        act1.setPositionControl(target_deg, speed)

except KeyboardInterrupt:
    pass
finally:
    conn.close()
    iface.close()
