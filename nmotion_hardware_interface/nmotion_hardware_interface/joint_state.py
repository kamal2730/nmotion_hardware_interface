import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import socket
import struct
import threading

HOST = "127.0.0.1"
PORT = 5005

class NMotionJointStatePublisher(Node):
    def __init__(self):
        super().__init__('nmotion_joint_state_publisher')

        self.publisher = self.create_publisher(JointState, '/joint_states', 10)

        self.joint_state = JointState()
        self.joint_state.name = ['joint1']

        self.angle = 0.0
        self.vel = 0.0
        self.effort = 0.0

        # socket client
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

        threading.Thread(target=self.socket_thread, daemon=True).start()

        self.timer = self.create_timer(0.015, self.timer_callback)

    def socket_thread(self):
        while True:
            data = self.sock.recv(24)  # 3 doubles
            if not data:
                break
            self.angle, self.vel, self.effort = struct.unpack("ddd", data)

    def timer_callback(self):
        self.joint_state.header.stamp = self.get_clock().now().to_msg()
        self.joint_state.position = [self.angle]
        self.joint_state.velocity = [self.vel]
        self.joint_state.effort = [self.effort]
        self.publisher.publish(self.joint_state)

    def destroy_node(self):
        self.sock.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = NMotionJointStatePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
