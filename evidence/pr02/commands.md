# PR02: команды и наблюдения

## Подготовка терминала

```bash
source /opt/ros/lyrical/setup.bash
export ROS_DOMAIN_ID=16
cd /work/snd_lab
ros2 pkg prefix turtlesim
```

Результат: активны `ROS_DISTRO=lyrical` и домен `16`; установленный пакет `turtlesim` найден в `/opt/ros/lyrical`.

## Сборка

```bash
set -o pipefail
colcon build --symlink-install --packages-select turtle_bringup 2>&1 | tee evidence/pr02/build.txt
```

Результат: `turtle_bringup` собран успешно; итог сохранён в `build.txt`.

## Launch и граф

```bash
source install/setup.bash
ros2 launch turtle_bringup sim.launch.py
ros2 node list --no-daemon --spin-time 2
```

Результат: launch запустил `/turtlesim`, а после `Ctrl+C` процесс `turtlesim_node` завершился cleanly.

## Доставка команды

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 1.0}, angular: {z: 0.5}}'
ros2 topic info /cmd_vel --verbose
ros2 topic info /turtle1/cmd_vel --verbose
```

Одна публикация на `/turtle1/cmd_vel` изменила позу с `(5.544, 5.544, 0.000)` до `(6.509, 5.797, 0.504)`. При ошибочном `/cmd_vel` был один publisher и ноль subscribers; у `/turtle1/cmd_vel` был subscriber `turtlesim`, но publisher отсутствовал. После исправления только полного имени на `/turtle1/cmd_vel` обнаружены один publisher и один subscriber, а поза изменилась; при остановленном издателе обе скорости снова равны нулю.

## Операторы и `source`

`>` перенаправляет stdout команды в файл, заменяя его прежнее содержимое. `|` передаёт stdout следующей команде; здесь `tee` одновременно показывает вывод и сохраняет его в `build.txt`.

`source` выполняет сценарий в текущей оболочке и сохраняет установленные им переменные окружения (`ROS_DISTRO`, пути ROS). Запуск отдельной программы создаёт дочерний процесс и не меняет окружение текущего терминала.

## Три использованные команды Linux

- `cd /work/snd_lab` — переход в корень workspace; результат: команды сборки и evidence выполнялись из `/work/snd_lab`.
- `colcon build --symlink-install --packages-select turtle_bringup` — собрать только пакет `turtle_bringup`; результат: один пакет собран успешно за 1.98 с.
- `ros2 topic info /turtle1/cmd_vel --verbose` — показать endpoints топика; результат после исправления: один publisher и один subscriber `turtlesim`.
