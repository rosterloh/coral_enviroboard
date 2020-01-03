#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from std_msgs.msg import Bool

#from display import ssd1306
import board
import digitalio
import Jetson.GPIO as GPIO

class EnviroBoard(Node):

    def __init__(self):
        super().__init__('enviroboard')
        self.setup_gpio()

        #self._display = ssd1306(height=32, rotate=2)

        self._button_pub = self.create_publisher(Bool, 'enviro_button',
                                                 qos_profile_sensor_data)
        self._led_sub = self.create_subscription(Bool, 'enviro_led',
                                                 self.led_callback, qos_profile_sensor_data)

        #self.timer = self.create_timer(
        #    1.0,  # unit: s
        #    self.timer_callback)
        
        self.get_logger().info('EnviroBoard setup and running on %s' % board.board_id)

    def setup_gpio(self):
        self._button = digitalio.DigitalInOut(board.D23)
        self._button.direction = digitalio.Direction.INPUT
        self._button.pull = digitalio.Pull.DOWN
        self._led = digitalio.DigitalInOut(board.D21)
        self._led.direction = digitalio.Direction.OUTPUT
        GPIO.add_event_detect(board.D23.id, GPIO.BOTH, 
                              callback=self.button_callback, bouncetime=10)

    def button_callback(self, channel):
        msg = Bool()
        msg.data = self._button.value
        self._button_pub.publish(msg)
        self.get_logger().info('Button {0}: "{1}"'.format(channel, "Pressed" if msg.data else "Released"))

    def led_callback(self, msg):
        self.get_logger().info('LED "{0}" requested'.format("ON" if msg.data else "OFF"))
        if msg.data:
            self._led.value = digitalio.Pin.HIGH
        else:
            self._led.value = digitalio.Pin.LOW

    #def timer_callback(self):
    #    msg = String()
    #    msg.data = 'Hello World: %d' % self.i
    #    self.publisher_.publish(msg)
    #    self.get_logger().info('Publishing: "%s"' % msg.data)
    #    self.i += 1


def main(args=None):
    rclpy.init(args=args)
    try:
        enviro = EnviroBoard()
        rclpy.spin(enviro)
    except KeyboardInterrupt:
        enviro.get_logger().info("ctrl-C detected, shutting down")
    finally:
        enviro.destroy_node()
        rclpy.shutdown()
        GPIO.cleanup()


if __name__ == '__main__':
    main()