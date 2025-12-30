from nmotion_transport import *
import socket
import struct
import time
import math
import threading

CMD_HOST = "127.0.0.1"
CMD_PORT = 6006     # FollowJointTrajectory input

STATE_HOST = "127.0.0.1"
STATE_PORT = 5005   # JointState output


# ------------------ NMotion Setup ------------------
iface = USBInterface("/dev/ttyACM0")
time.sleep(2)
act1 = Actuator(0, iface)
time.sleep(2)

status, zero_offset_deg = act1.getZeroPosition()
if not status:
    zero_offset_deg = 0.0

print("NMotion initialized")

# Mutex to protect actuator access
act_lock = threading.Lock()


# ------------------ Command Server ------------------
def command_thread():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((CMD_HOST, CMD_PORT))
    sock.listen(1)

    print("Waiting for ROS FollowJointTrajectory client...")
    conn, _ = sock.accept()
    print("Trajectory client connected")

    try:
        while True:
            data = conn.recv(16)  # angle_rad + speed_deg
            if not data:
                break

            target_rad, speed = struct.unpack("dd", data)
            target_deg = math.degrees(target_rad)

            with act_lock:
                act1.setPositionControl(target_deg, speed)

    except Exception as e:
        print("Command thread error:", e)
    finally:
        conn.close()
        sock.close()


# ------------------ State Publisher ------------------
def state_thread():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((STATE_HOST, STATE_PORT))
    sock.listen(1)

    print("Waiting for ROS JointState client...")
    conn, _ = sock.accept()
    print("JointState client connected")

    try:
        while True:
            with act_lock:
                status, angle_deg = act1.getOutputPosition()
                if not status:
                    continue

                angle_rad = math.radians(angle_deg - zero_offset_deg)

                status, vel_deg = act1.getOutputVelocity()
                vel_rad = math.radians(vel_deg) if status else 0.0

                status, torque_nm = act1.getOutputTorque()
                effort = torque_nm if status else 0.0

            data = struct.pack("ddd", angle_rad, vel_rad, effort)
            conn.sendall(data)

            time.sleep(0.02)  # 50 Hz

    except Exception as e:
        print("State thread error:", e)
    finally:
        conn.close()
        sock.close()


# ------------------ Main ------------------
try:
    t_cmd = threading.Thread(target=command_thread, daemon=True)
    t_state = threading.Thread(target=state_thread, daemon=True)

    t_cmd.start()
    t_state.start()

    print("NMotion driver running (command + state)")

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Shutting down driver")

finally:
    iface.close()
