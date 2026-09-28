# ROS 2 practices

Workspace for the Robotics course practical assignments.

## PR02: `turtle_bringup`

The package installs `sim.launch.py`, which starts the standard `turtlesim_node`.

## Local run

```bash
source /opt/ros/lyrical/setup.bash
export ROS_DOMAIN_ID=16
colcon build --symlink-install --packages-select turtle_bringup
source install/setup.bash
ros2 launch turtle_bringup sim.launch.py
```

`turtle_bringup` contains a launch description, not a custom ROS node.

## CI

GitHub Actions builds the package, verifies that the launch file is installed, and checks PR02 evidence with the pinned course kit.
