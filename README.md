# `coral_enviroboard`

A ROS2 driver for the Coral Environmental Sensor Board.

## Nodes

### enviroboard

#### Published Topics

* `/enviro_button` - `std_msgs/Bool`

    Button pressed and released.

* `/enviro_led` - `std_msgs/Bool`

Usage:
~~~
ros2 run coral_enviroboard enviroboard
~~~

Requirements:
* ROS2, tested with Eloquent
* Python 3, tested with 3.6