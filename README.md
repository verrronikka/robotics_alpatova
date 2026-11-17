# ПР05. Launch, QoS и повтор записи

Ubuntu 24.04.3 LTS под WSL2, ROS 2 Jazzy.

Продолжен пакет patrol из ПР04, сохранён turtle_bringup.
Новый course_bringup запускает всю систему одной командой.

## Окружение и сборка

В свежем терминале Ubuntu, до подключения install/setup.bash:

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=16
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
cd /root/robotics-inspect
colcon build --symlink-install
source install/setup.bash
```

В каждом дополнительном терминале нужны те же настройки окружения
и подключение install/setup.bash.

## Запуск

```bash
ros2 launch course_bringup patrol.launch.py \
  namespace:=robot_a subscriber_reliability:=best_effort record:=false
```

Аргументы launch:

| Аргумент | По умолчанию | Назначение |
| --- | --- | --- |
| namespace | robot_a | Пространство имён наших нод |
| subscriber_reliability | best_effort | reliable или best_effort |
| record | false | Включение recorder через IfCondition |
| bag_dir | evidence/pr05/bag | Каталог новой записи |

Глобальный /turtlesim публикует /turtle1/pose.
В /robot_a работают patrol, pose_relay и pose_subscriber.
Выход cmd_vel ноды patrol переназначен в /turtle1/cmd_vel.
Входные имена топиков внутри наших нод относительные;
связи с глобальным turtlesim заданы в launch.

pose_relay передаёт Pose в /robot_a/sensor_pose с best_effort.
pose_subscriber считает доставленные сообщения и выводит received.
Параметр subscriber_reliability применяется при запуске ноды.

Для новой записи укажите свободный каталог:

```bash
ros2 launch course_bringup patrol.launch.py \
  namespace:=robot_a subscriber_reliability:=best_effort \
  record:=true bag_dir:=evidence/pr05/new-bag
```

Остановка через Ctrl+C завершает запись и сохраняет metadata.yaml.

## Эксперимент с QoS

При subscriber_reliability:=reliable топик присутствовал,
но received оставался 0. Диагностика указала несовместимость RELIABILITY.
Reliable echo завершился по timeout с кодом 124.
Контрольный best_effort echo получил сообщение с кодом 0.

После выбора best_effort счётчик подписчика рос,
а best_effort echo получил сообщение с кодом 0.

Сохранённый bag содержит только /robot_a/sensor_pose:
1222 сообщения turtlesim/msg/Pose за 19.538207750 с, формат MCAP.

Перед replay живой launch остановлен:

```bash
ros2 bag play evidence/pr05/bag \
  --qos-profile-overrides-path config/qos-overrides.yaml --loop
```

Для каждого профиля читателя тот же bag запускался заново.
Reliable echo дал код 124, best_effort echo — сообщение и код 0.
В обеих проверках работал только rosbag2_player.
Хеши bag и YAML совпали; менялось требование читателя.

## Проверки и материалы

```bash
colcon test --python-testing pytest --event-handlers console_direct+ \
  --return-code-on-test-failure
colcon test-result --verbose
python3 .course-kit/v1/tools/check_practice.py PR05 --submission .
```

Подтверждённый результат colcon: 38 тестов, 0 ошибок,
0 падений, 3 пропуска.

- [Диагностика до исправления, включая replay](evidence/pr05/qos-before.txt)
- [Диагностика после исправления, включая replay](evidence/pr05/qos-after.txt)
- [Метаданные записи](evidence/pr05/bag-metadata.yaml)
- [Декларация использования ИИ](AI_USAGE.md)
- [Материалы ПР04](evidence/pr04/parameters.md)

Course kit: v1-w11.
SHA-256 архива:
0b67bfd41448549d21122124b7f49211ba2cd068cc56751871f319eadeb9d0ab

## Источники

- [Задание ПР05](https://ros.lms.ci.nsu.ru/practices/pr05)
- Лекция 05: страницы 4–6, 8–12, 14.
- [ROS 2 Jazzy: QoS](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html)
- [ROS 2 Jazzy: rosbag2 QoS overrides](https://docs.ros.org/en/jazzy/How-To-Guides/Overriding-QoS-Policies-For-Recording-And-Playback.html)

## ПР06: модель робота, tf2 и QoS преобразований

Пакет `course_description` содержит:
- `urdf/vehicle.urdf.xacro` — корпус и фиксированные крепления сенсоров;
- `urdf/wheels.xacro` — параметры, колёса и рулевые шарниры;
- `launch/description.launch.py` — запуск robot_state_publisher;
- `rviz/model.rviz` — отображение модели и систем координат;
- `test/test_model.py` — проверки дерева, креплений и геометрии.

Размеры взяты из `models/course_ackermann/model.sdf` course kit:
база 0.8 м, колея 0.62 м, радиус колеса 0.12 м, ширина 0.07 м.
Камера, лидар и IMU закреплены непосредственно на base_link;
каждое крепление имеет xyz=(0.28, 0, 0.38) м и нулевой поворот.

Дополнительно требуются xacro, robot_state_publisher, rviz2,
ament_cmake_pytest и check_urdf. Gazebo для этой работы не требуется.

### Сборка и запуск модели

В свежем терминале Ubuntu, подключив только базовую ROS:

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=16
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
cd /root/robotics-inspect
colcon build --symlink-install
```

После успешной сборки:

```bash
source install/setup.bash
ros2 launch course_description description.launch.py
```

В каждом дополнительном терминале повторить подключение базовой ROS,
обе переменные окружения, переход в workspace и `source install/setup.bash`.

Для появления всех подвижных звеньев публиковать положения шарниров
в отдельном терминале, оставляя publisher работать:

```bash
ros2 topic pub --rate 10 /joint_states sensor_msgs/msg/JointState \
  "{header: auto, name: [front_left_steering_joint, front_right_steering_joint, front_left_wheel_joint, front_right_wheel_joint, rear_left_wheel_joint, rear_right_wheel_joint], position: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}"
```

Открыть RViz в другом терминале:

```bash
ros2 run rviz2 rviz2 -d \
  "$(ros2 pkg prefix course_description)/share/course_description/rviz/model.rviz"
```

В конфигурации выбран Fixed Frame=base_link.
RobotModel получает /robot_description с reliable + transient local.
Фиксированные связи публикуются сразу в /tf_static;
подвижные связи появляются в /tf после получения /joint_states.
У каждой связи один владелец — robot_state_publisher.

### Проверки ПР06

```bash
xacro src/course_description/urdf/vehicle.urdf.xacro > /tmp/pr06-vehicle.urdf
check_urdf /tmp/pr06-vehicle.urdf
colcon test --packages-select course_description \
  --event-handlers console_direct+ --return-code-on-test-failure
colcon test-result --test-result-base build/course_description --verbose
```

Тесты проверяют связность дерева, единственный корень base_link,
родителей и смещения сенсоров, положения осей, геометрию колёс
и допустимость числовых значений масс и компонентов инерции.

Эксперимент с дефектом: в отдельной ветке назначить camera_link
родителем lidar_link, сохранив прежний offset.
Проверка структуры может принять такое дерево;
test_sensor_mounts[lidar_link] должен обнаружить неверного родителя.
После возврата связи повторить ту же проверку.

Для опыта с durability запускать поздние подписки /tf_static
с явно заданными reliable + transient_local и reliable + volatile.
Во время опыта издатель должен продолжать работать;
повторный запуск издателя может доставить volatile-подписчику новое сообщение.

Материалы проверки сохраняются в `evidence/pr06/`.
Course kit и SHA-256 архива совпадают с указанными выше для v1-w11.

Источники:
- https://ros.lms.ci.nsu.ru/practices/pr06
- Лекция 06: страницы 3, 11–16, 18–19.
- https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Tf2.html
- https://docs.ros.org/en/jazzy/p/robot_state_publisher/
