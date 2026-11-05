# ПР01. Окружение и граф ROS 2

## Среда

Опыт выполнен в WSL2: Ubuntu 24.04.3 LTS, ROS 2 Jazzy.
Gazebo не установлен: команда `gz sim --versions` завершилась сообщением `gz: command not found`. Для этого опыта с turtlesim Gazebo не понадобился.
RMW: `rmw_fastrtps_cpp`. Вывод `ros2 doctor --report` сохранён в [doctor.txt](doctor.txt).

## Исправный граф: домен 16

В терминале A запущен `ros2 run turtlesim turtlesim_node`, в терминале B — `ros2 run turtlesim turtle_teleop_key`. Оба процесса работают с `ROS_DOMAIN_ID=16`. Наблюдения выполнялись из терминала C в том же домене.

Команда `ros2 node list --no-daemon --spin-time 2` обнаружила:

- `/teleop_turtle`
- `/turtlesim`

Команда `ros2 topic list -t` показала:

- `/parameter_events` — `rcl_interfaces/msg/ParameterEvent`
- `/rosout` — `rcl_interfaces/msg/Log`
- `/turtle1/cmd_vel` — `geometry_msgs/msg/Twist`
- `/turtle1/color_sensor` — `turtlesim/msg/Color`
- `/turtle1/pose` — `turtlesim/msg/Pose`

`/teleop_turtle` публикует команды скорости в `/turtle1/cmd_vel`. `/turtlesim` принимает их и публикует позу в `/turtle1/pose`.

Команда `ros2 topic type /turtle1/pose` вернула `turtlesim/msg/Pose`. Команда `ros2 topic echo /turtle1/pose --once` получила начальную позу:

- x: 5.544444561004639
- y: 5.544444561004639
- theta: 0.0
- linear_velocity: 0.0
- angular_velocity: 0.0

Частота `/turtle1/pose` измерялась 12,16 секунды. В замере получено около 62,5 Гц. Полный вывод и время запуска записаны в [pose-hz.txt](pose-hz.txt). Код `124` в конце этого файла означает остановку команды по заданному таймауту.

## Разрыв связи: домен 17

Симулятор A оставался в домене 16. Teleop был остановлен и запущен заново в домене 17. Проверка из терминала C также выполнялась в домене 17.

Команда `ros2 node list --no-daemon --spin-time 2` показала только `/teleop_turtle`; `/turtlesim` не обнаружилась. Проверка позы ждала 5 секунд, сообщение не пришло, код завершения — `124`.

## Восстановление: домен 16

Teleop был остановлен и запущен заново с `ROS_DOMAIN_ID=16`. В терминале C тоже был установлен домен 16. Снова обнаружились `/teleop_turtle` и `/turtlesim`. Проверка получила сообщение Pose и завершилась с кодом `0`.

При чтении появилось предупреждение `A message was lost!!!`, но затем пришло сообщение с позой:

- x: 8.798375129699707
- y: 0.0
- theta: -0.7951853275299072
- linear_velocity: 0.0
- angular_velocity: 0.0

## Причина

`ROS_DOMAIN_ID` задаёт область обнаружения участников ROS 2. Teleop и CLI-подписчик в домене 17 не обнаруживали симулятор из домена 16. Команда `export` меняет окружение оболочки, но не перенастраивает уже запущенную ноду — поэтому teleop пришлось остановить и запустить заново. Возврат teleop и CLI в домен 16 восстановил получение позы.
