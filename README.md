# ПР02. Пакет и запуск turtlesim

Работа выполнена в Ubuntu 24.04.3 LTS под WSL2.
ROS 2 Jazzy, RMW rmw_fastrtps_cpp, ROS_DOMAIN_ID=16.

## Содержание

Пакет turtle_bringup устанавливает launch-файл для запуска готовой ноды
turtlesim_node. Собственная нода с callback в ПР02 не создаётся.

- src/turtle_bringup/ — исходники и метаданные пакета.
- evidence/pr02/ — логи, наблюдения и отчёт.
- .github/workflows/ci.yml — GitHub Actions.

## Сборка

Из корня репозитория в новом терминале:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select turtle_bringup
python3 -m py_compile src/turtle_bringup/launch/sim.launch.py
```

## Запуск

В отдельном терминале, из корня репозитория:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
ros2 pkg prefix turtle_bringup
ls "$(ros2 pkg prefix turtle_bringup)/share/turtle_bringup/launch"
ros2 launch turtle_bringup sim.launch.py
```

Перед запуском следует завершить предыдущие экземпляры turtlesim и teleop.

В другом терминале с тем же окружением:

```bash
ros2 node list --no-daemon --spin-time 2
```

Во время запуска обнаружена /turtlesim.
После Ctrl+C в терминале launch нода исчезла из графа.

## Команда движения

В терминале наблюдения подключить ту же ROS, домен и RMW.

```bash
ros2 interface show geometry_msgs/msg/Twist
ros2 topic type /turtle1/pose
ros2 topic echo /turtle1/pose turtlesim/msg/Pose --once

ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'

sleep 2
ros2 topic echo /turtle1/pose turtlesim/msg/Pose --once
```

Черепашка выполнила движение вперёд с поворотом.
Поза изменилась; после прекращения команд скорости стали нулевыми.

## Сбой и исправление

Ошибочный издатель:

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

Пока он работает, в другом терминале:

```bash
ros2 topic info /cmd_vel --verbose
ros2 topic info /turtle1/cmd_vel --verbose
```

У /cmd_vel обнаружен один издатель и нет подписчиков.
У /turtle1/cmd_vel — один подписчик и нет издателей.
Черепашка неподвижна, две полученные позы совпали.

Остановить ошибочного издателя через Ctrl+C.
Исправить только имя топика:

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

При повторной проверке у /turtle1/cmd_vel обнаружены один издатель
и один подписчик. Черепашка двигалась со скоростями 1.0 и 0.5.
После Ctrl+C издателя и ожидания 2 секунд обе скорости стали нулевыми.

Причина сбоя: /cmd_vel и /turtle1/cmd_vel — разные полные имена.
Одинакового типа Twist недостаточно для обмена между разными топиками.

## Результаты и объяснения

- [Команды и наблюдения](evidence/pr02/commands.md).
- [Типы сообщений](evidence/pr02/types.md).
- [Сборка пустого пакета](evidence/pr02/build-empty.txt).
- [Итоговая сборка](evidence/pr02/build.txt).

## Автоматическая проверка

Используется course kit v1-w09.

SHA-256 архива:
8579e0afe96d76220735b6019cc38b1f3cac8c21e4aae8470785138a74a6c54a

После подготовки report.json и AI_USAGE.md:

```bash
python3 .course-kit/v1/tools/check_practice.py PR02 --submission .
```

Workflow GitHub Actions собирает turtle_bringup в контейнере ROS 2 Jazzy,
проверяет наличие установленного sim.launch.py, синтаксис Python
и комплект сдачи через checker.

Движение черепашки и остановка launch проверены локально в WSL2.

## Источники

- [Задание ПР02](https://ros.lms.ci.nsu.ru/practices/pr02).
- Лекция 02, стр. 2, 4, 11–18: терминал, граф, пакет, сборка и launch.
- [Topics vs Services vs Actions](https://docs.ros.org/en/iron/How-To-Guides/Topics-Services-Actions.html).
- Ссылки на документацию Jazzy приведены в evidence/pr02/commands.md.

Использование ИИ описывается в AI_USAGE.md.

## ПР03. Первая собственная нода

Пакет `patrol` использует `ament_python` и устанавливает команду
`ros2 run patrol patrol`. Имя работающей ноды — `/patrol`.

### Окружение

В каждом новом терминале Ubuntu:

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=16
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
cd /root/robotics-inspect
```

### Сборка и тесты

Сборка выполняется в свежем терминале с базовой ROS:

```bash
colcon build --symlink-install
source install/setup.bash
colcon test --python-testing pytest --event-handlers console_direct+ \
  --return-code-on-test-failure
colcon test-result --verbose
```

### Демонстрация

В двух отдельных терминалах подключить окружение выше
и выполнить `source install/setup.bash`.

В первом терминале запустить симулятор:

```bash
ros2 launch turtle_bringup sim.launch.py
```

Во втором запустить ошибочный вариант:

```bash
ros2 run patrol patrol
```

Он публикует в `/cmd_vel`, тогда как turtlesim слушает `/turtle1/cmd_vel`.
После остановки patrol через Ctrl+C запустить исправленный вариант:

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Подписка на `/turtle1/pose` типа `turtlesim/msg/Pose` сохраняет последнее
сообщение. Таймер с периодом 0.1 с публикует `geometry_msgs/msg/Twist`.
До первой позы команда нулевая; после получения позы
`linear.x=0.5`, `angular.z=0.3`, остальные компоненты нулевые.

Функция `command_from_pose` проверяется без запуска ROS-нод:
отсутствие позы даёт нулевую команду, полученная поза — команду движения.
Также проверяется сохранность входной позы.

При Ctrl+C публикация прекращается. Нода не отправляет отдельную
нулевую команду при завершении; turtlesim останавливается по своему
таймауту команд.

### Файлы и проверки

- `src/patrol/patrol/patrol.py` — нода и чистая функция выбора команды.
- `src/patrol/test/test_command.py` — тесты поведения.
- `src/patrol/package.xml` — зависимости ROS.
- `src/patrol/setup.py` и `setup.cfg` — установка пакета и команды.
- `evidence/pr03/` — реальные логи и отчёт.
- `AI_USAGE.md` — декларация помощи ИИ.

Текущий workflow GitHub Actions собирает оба пакета в ROS 2 Jazzy,
проверяет установленный launch, выполняет тесты и checker PR03.
После заполнения отчёта локальная проверка:

```bash
python3 .course-kit/v1/tools/check_practice.py PR03 --submission .
```

Course kit: `v1-w09`, SHA-256 архива:
`8579e0afe96d76220735b6019cc38b1f3cac8c21e4aae8470785138a74a6c54a`.

Источники: задание https://ros.lms.ci.nsu.ru/practices/pr03;
лекция 03, стр. 3–17; официальная документация ROS 2 Jazzy
по созданию Python-пакета, издателю и подписчику.
