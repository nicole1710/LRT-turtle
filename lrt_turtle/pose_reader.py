import math
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from turtlesim.srv import SetPen


class PoseReader(Node):
    def __init__(self):
        super().__init__('pose_reader')
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )
        self.pen_client = self.create_client(
            SetPen,
            '/turtle1/set_pen'
        )
        self.publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )
        self.strokes = [
            # L
            [(1.25, 10.0), (1.25, 6.0)],
            [(1.25, 6.0), (3.25, 6.0)],

            # R
            [(4.5, 10.0), (4.5, 6.0)],  # pionowa
            [(4.5, 10.0), (6.5, 10.0)],  # u pozioma
            [(6.5, 10.0), (6.5, 8.0)],  # r pion
            [(6.5, 8.0), (4.5, 8.0)],  # m pozi
            [(5.5, 8.0), (6.5, 6.0)],  # ukosna

            # T
            [(7.75, 10.0), (9.75, 10.0)],  # u poz
            [(8.75, 10.0), (8.75, 6.0)],  # pion

            # N
            [(2.875, 1.0), (2.875, 5.0)],
            [(2.875, 5.0), (4.875, 1.0)],
            [(4.875, 1.0), (4.875, 5.0)],

            # P
            [(6.125, 1.0), (6.125, 5.0)],
            [(6.125, 5.0), (8.125, 5.0)],
            [(8.125, 5.0), (8.125, 3.0)],
            [(8.125, 3.0), (6.125, 3.0)]
        ]
        self.current_stroke = 0
        self.current_point = 0
        self.drawing = False
        self.finished = False
        self.pen_down = False
        self.pen_busy = False
        self.pen_initialized = False
        self.initializing_pen = False
        self.set_pen(1)

    def move(self, linear, angular):
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular
        self.publisher.publish(msg)

    def pose_callback(self, msg):
        self.get_logger().info(
            f'x={msg.x:.2f}, y={msg.y:.2f}, theta={msg.theta:.2f}'
        )
        if self.pen_busy:
            return
        if self.finished:
            return
        if not self.pen_initialized:
            self.set_pen(1)
            return

        self.get_logger().info(
            f'drawing={self.drawing}, pen_busy={self.pen_busy}, '
            f'stroke={self.current_stroke}, point={self.current_point}'
        )

        if self.current_stroke >= len(self.strokes):
            self.get_logger().info('Finished all strokes!')
            return

        target_x, target_y = self.strokes[self.current_stroke][self.current_point]
        dx = target_x - msg.x
        dy = target_y - msg.y
        d = distance(msg.x, msg.y, target_x, target_y)

        if d < 0.00001:
            self.move(0.0, 0.0)

            if self.current_point == 0 and not self.drawing:
                self.set_pen(0)
                return

            if self.current_point == 0 and not self.pen_down:
                return

            # koniec biezacej kreski
            if self.current_point == len(self.strokes[self.current_stroke]) - 1:
                if self.current_stroke == len(self.strokes) - 1:
                    self.set_pen(1)
                    self.drawing = False
                    self.finished = True
                    self.get_logger().info('Finished all strokes!')
                    return
                else:
                    # sa jeszcze kolejne kreski
                    self.set_pen(1)
                    self.drawing = False
                    self.current_stroke += 1
                    self.current_point = 0
            else:
                # To nie koniec kreski - przechodzimy do nastepnego punktu
                self.current_point += 1
            return

        target_theta = math.atan2(dy, dx)

        angle_error = math.atan2(
            math.sin(target_theta - msg.theta),
            math.cos(target_theta - msg.theta)
        )
        if self.pen_down and abs(angle_error) > 0.01:
            self.get_logger().warning(
                f'ROTACJA Z PISAKIEM: d={d:.4f}, '
                f'angle_error={angle_error:.4f}'
            )
        if abs(angle_error) > 0.01:
            self.move(0.0, 1.5 * angle_error)
        else:
            self.move(min(0.75, 0.5 * d), 0.0)

    def set_pen(self, off):
        if not self.pen_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warning('Pen service is not available')
            return
        request = SetPen.Request()
        request.r = 255
        request.g = 255
        request.b = 255
        request.width = 3
        request.off = off

        if off == 1 and not self.pen_initialized:
            self.initializing_pen = True

        self.pen_busy = True  # czekamy na zmiane pisaka
        # call_async(request) - wyslanie zadania do uslugi
        future = self.pen_client.call_async(request)
        future.add_done_callback(
            lambda future:
            self.pen_response_callback(future, off)
        )

    def pen_response_callback(self, future, off):
        try:
            future.result()

            self.pen_down = (off == 0)
            self.drawing = self.pen_down

            if self.initializing_pen and off == 1:
                self.pen_initialized = True
                self.initializing_pen = False

            self.get_logger().info(
                f'Pen service completed. pen_down={self.pen_down}'
            )

        except Exception as e:
            self.get_logger().error(f'Pen service failed: {e}')

        finally:
            self.pen_busy = False


def distance(x, y, target_x, target_y):
    dx = target_x-x
    dy = target_y-y
    d = math.sqrt(dx**2+dy**2)
    return d


def main(args=None):
    rclpy.init(args=args)
    node = PoseReader()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
