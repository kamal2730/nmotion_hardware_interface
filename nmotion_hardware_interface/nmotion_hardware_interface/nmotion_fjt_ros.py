import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from control_msgs.action import FollowJointTrajectory
import socket
import struct
import time
import math

HOST = "127.0.0.1"
PORT = 6006

class NMotionFJT(Node):
    def __init__(self):
        super().__init__('nmotion_follow_joint_trajectory')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

        self._action_server = ActionServer(
            self,
            FollowJointTrajectory,
            '/follow_joint_trajectory',
            self.execute_callback
        )

    def execute_callback(self, goal_handle):
        traj = goal_handle.request.trajectory
        prev_time = 0.0

        for point in traj.points:
            target_rad = point.positions[0]

            # compute speed (deg/s)
            dt = point.time_from_start.sec - prev_time
            dt = max(dt, 0.01)
            speed_deg = abs(math.degrees(target_rad)) / dt

            self.sock.sendall(struct.pack("dd", target_rad, speed_deg))

            time.sleep(dt)
            prev_time = point.time_from_start.sec

        goal_handle.succeed()
        return FollowJointTrajectory.Result()

    def destroy_node(self):
        self.sock.close()
        super().destroy_node()


def main():
    rclpy.init()
    node = NMotionFJT()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
