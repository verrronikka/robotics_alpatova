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
