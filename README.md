# LRT Turtle

Wezel ROS 2 w jezyku Python sterujacy zolwiem w symulatorze turtlesim. Program rysuje napis LRT oraz inicjaly autora ponizej.

## Wymagania

- Ubuntu 22.04
- ROS 2 Humble
- Python 3
- turtlesim

## Budowanie paczki

```bash
source /opt/ros/humble/setup.bash
cd ~/lrt_ws
colcon build --packages-select lrt_turtle
source install/setup.bash
```

## Uruchamianie

W pierwszym terminalu uruchom symulator:

```bash
source /opt/ros/humble/setup.bash
ros2 run turtlesim turtlesim_node
```

W drugim terminalu uruchom wezel rysujacy:

```bash
source /opt/ros/humble/setup.bash
cd ~/lrt_ws
source install/setup.bash
ros2 run lrt_turtle pose_reader
```

## Interfejsy ROS 2

- Subskrypcja: `/turtle1/pose` (`turtlesim/msg/Pose`)
- Publikacja: `/turtle1/cmd_vel` (`geometry_msgs/msg/Twist`)
- Serwis: `/turtle1/set_pen` (`turtlesim/srv/SetPen`)


## Sposob sterowania

Wezel wykorzystuje aktualna pozycje i orientacje zolwia do wyznaczania kierunku ruchu oraz odleglosci od kolejnego punktu docelowego. Sterowanie jest realizowane na
podstawie informacji zwrotnej z tematu `/turtle1/pose`. Podczas przechodzenia miedzy odcinkami program korzysta z serwisu `/turtle1/set_pen`,
aby podnosic i opuszczac pioro.
