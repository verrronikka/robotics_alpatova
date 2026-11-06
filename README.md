# ПР03. Первая нода: поза и команда

Работа выполнена в Ubuntu 24.04.3 LTS под WSL2, ROS 2 Jazzy.

## Окружение

В каждом новом терминале:

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=16
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
cd /root/robotics-inspect
```

## Сборка и тесты

В свежем терминале после подключения базовой ROS:

```bash
colcon build --symlink-install
source install/setup.bash
colcon test --python-testing pytest --event-handlers console_direct+ \
  --return-code-on-test-failure
colcon test-result --verbose
```

## Запуск

В первом терминале подключить окружение и запустить симулятор
через сохранённый пакет turtle_bringup:

```bash
source install/setup.bash
ros2 launch turtle_bringup sim.launch.py
```

Во втором терминале подключить окружение и запустить patrol:

```bash
source install/setup.bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Перед опытом остановить лишние экземпляры patrol и teleop.

## Работа ноды

Нода /patrol подписывается на /turtle1/pose типа turtlesim/msg/Pose.
Callback подписки только сохраняет последнее сообщение.

Таймер с периодом 0.1 с публикует geometry_msgs/msg/Twist.
До первой позы команда нулевая; после получения позы
linear.x=0.5, angular.z=0.3. Остальные компоненты нулевые.

Чистая функция command_from_pose проверяется двумя тестами:
отсутствие позы и полученная поза. Также проверяется сохранность
входной позы.

## Дефект и исправление

Запуск без remap:

```bash
ros2 run patrol patrol
```

Нода публикует в /cmd_vel, а turtlesim слушает /turtle1/cmd_vel.
Команда формируется, но черепашка неподвижна.

После остановки ошибочного экземпляра remap при повторном запуске
соединяет издателя и подписчика. Движение восстановлено.
Измеренная частота команды — около 10 Гц.

Ctrl+C завершает patrol и прекращает публикацию. Нода не отправляет
отдельный нулевой Twist; turtlesim останавливается по своему
таймауту команд. После ожидания проверены нулевые скорости
и неизменность позы.

## Файлы и результаты

- src/patrol/patrol/patrol.py — нода и чистая функция выбора команды.
- src/patrol/test/test_command.py — тесты поведения.
- src/patrol/package.xml — зависимости ROS.
- src/patrol/setup.py и setup.cfg — установка пакета и команды.
- [Демонстрация и объяснения](evidence/pr03/demo.md).
- [Тесты](evidence/pr03/tests.txt).
- [Итоговые результаты colcon](evidence/pr03/test-result.txt).
- [Отчёт](evidence/pr03/report.json).
- [Декларация помощи ИИ](AI_USAGE.md).

Локально собраны оба пакета: 8 тестов, 0 ошибок, 0 падений,
2 пропуска стандартных copyright-тестов.

## Автоматическая проверка

GitHub Actions собирает пакеты, проверяет установленный launch,
выполняет тесты и checker PR03.

```bash
python3 .course-kit/v1/tools/check_practice.py PR03 --submission .
```

Course kit: v1-w09.
SHA-256 архива:
8579e0afe96d76220735b6019cc38b1f3cac8c21e4aae8470785138a74a6c54a.

## Источники

- [Задание ПР03](https://ros.lms.ci.nsu.ru/practices/pr03).
- Лекция 03, стр. 3–17.
- [Создание пакета](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html).
- [Python publisher/subscriber](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html).
