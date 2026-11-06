# ПР03. Первая нода: поза и команда

## Окружение и реализация

Ubuntu 24.04.3 LTS в WSL2, ROS 2 Jazzy.
ROS_DOMAIN_ID=16, RMW_IMPLEMENTATION=rmw_fastrtps_cpp.
Gazebo не используется и не установлен.

Коммит реализации: 24d2c74f7d516a01bf3d78f813f523d0621e5c08.

Пакет patrol находится рядом с сохранённым turtle_bringup.
Подписка /turtle1/pose имеет тип turtlesim/msg/Pose.
Callback on_pose только сохраняет сообщение в latest_pose.
Подписка, издатель и таймер хранятся в полях объекта.

Таймер с периодом 0.1 с публикует geometry_msgs/msg/Twist.
Чистая функция command_from_pose до первой позы возвращает
нулевую команду, после получения позы — linear.x=0.5,
angular.z=0.3. Остальные компоненты нулевые.

## Сбой

Симулятор запущен через ros2 launch turtle_bringup sim.launch.py.
Нода запущена без remap:

```bash
ros2 run patrol patrol
```

/patrol публиковала в /cmd_vel: один издатель, ноль подписчиков.
В /turtle1/cmd_vel были ноль издателей и один подписчик turtlesim.
В /cmd_vel получена команда linear.x=0.5, angular.z=0.3,
но черепашка оставалась неподвижной: обе скорости в Pose равны нулю.

Причина: относительное cmd_vel в корневом namespace разрешается
в /cmd_vel. Это другое полное имя, чем /turtle1/cmd_vel.
Совпадения типа сообщения недостаточно для связи.

Логи: broken-node.txt, broken-cmd-vel.txt,
broken-turtle-cmd-vel.txt, broken-command.txt, broken-pose.txt.

## Исправление

Ошибочный экземпляр остановлен через Ctrl+C. Повторный запуск:

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Код не менялся: remap изменил имя выходного топика.
В /turtle1/cmd_vel обнаружены издатель patrol и подписчик turtlesim.
Пользователь наблюдал движение. В Pose получены скорости
linear_velocity=0.5, angular_velocity=0.30000001192092896.

Во время 10-секундного запуска ros2 topic hz наблюдались
средние частоты 10.000–10.003 Гц; последняя оценка — 10.001 Гц.
Интервалы сообщений находились примерно в пределах 0.099–0.101 с.
10 секунд включают запуск CLI и обнаружение потока.

Логи: fixed-node.txt, fixed-endpoints.txt, fixed-command.txt,
fixed-pose.txt, command-hz.txt.

## Остановка

После Ctrl+C в терминале patrol и ожидания 2 секунд
в графе осталась /turtlesim, издателей команды стало ноль.
В двух сообщениях Pose, разделённых дополнительным ожиданием,
координаты и угол совпали; обе скорости были нулевыми.

Завершение patrol прекращает публикацию, но само по себе
не отправляет нулевой Twist. Симулятор останавливается
по своему таймауту команд.

Логи: stopped-nodes.txt, stopped-endpoints.txt,
stopped-pose-1.txt, stopped-pose-2.txt.

## Выполнение программы

- rclpy.init создаёт контекст ROS для работы программы.
- rclpy.spin запускает обработку событий исполнителем.
- Callback подписки сохраняет позу; callback таймера публикует команду.
- Ctrl+C прерывает ожидание; finally освобождает ноду и завершает контекст.

## Проверки

Минимальная нода появилась в графе до добавления подписки и таймера.
Подписка и поток позы проверены через node info, topic info и echo.

Два теста чистой функции прошли: отсутствие позы и полученная поза.
Проверены все компоненты команды и сохранность входной позы.
Узлы ROS для этих тестов не запускались.

Первый pytest-прогон выявил две ошибки порядка импортов.
После исправления: 4 passed, 1 skipped.
tests.txt содержит успешный прогон из src/patrol;
tests-first-run.txt сохраняет исходный неуспешный прогон.

Итоговая сборка: оба пакета собраны.
Итоговый colcon test-result: 8 tests, 0 errors, 0 failures, 2 skipped.
Пропущены стандартные copyright-тесты шаблонов пакетов.
Предупреждения flake8 о fork не привели к падению проверок.

Логи: build.txt, colcon-test.txt, test-result.txt.

## Источники

- https://ros.lms.ci.nsu.ru/practices/pr03
- Лекция 03: стр. 3–7 — пакет и запуск; 8–13 — события, подписка и таймер;
  14–17 — имена топиков, проверка графа и remap.
- https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html
- https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html
