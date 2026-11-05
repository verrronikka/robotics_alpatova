# ПР02: команды и результаты

## Окружение

Ubuntu 24.04.3 LTS в WSL2, пользователь root.
ROS 2 Jazzy, ROS_DOMAIN_ID=16, RMW_IMPLEMENTATION=rmw_fastrtps_cpp.
Корень workspace: /root/robotics-inspect.
Пакет: turtle_bringup, тип сборки ament_python.

## Три команды Linux

| Команда | Назначение | Мой результат |
|---|---|---|
| `pwd` | Показать текущий каталог | `/root/robotics-inspect` |
| `mkdir -p src evidence/pr02` | Создать каталоги исходников и результатов | Каталоги созданы |
| `ls -la src` | Показать содержимое src, включая скрытые записи | До генерации пакета каталог был пустым, кроме `.` и `..` |

## Оболочка и потоки вывода

`source /opt/ros/jazzy/setup.bash` выполняет настройки в текущей оболочке.
Изменения окружения остаются доступны следующим командам этого терминала.
Обычная внешняя программа выполняется отдельным процессом и не может
напрямую изменить окружение родительской оболочки.

`source install/setup.bash` подключает собранный workspace поверх базовой ROS.
Сама команда source не запускает turtlesim.

`export ROS_DOMAIN_ID=16` передаёт настройку домена запускаемым процессам.

Оператор `>` записывает стандартный вывод в файл, заменяя прежнее содержимое.
Оператор `|` передаёт стандартный вывод следующей команде.
`2>&1` направляет ошибки туда же, куда стандартный вывод.
`tee файл` одновременно показывает поступивший вывод и записывает его в файл.
`set -o pipefail` делает статус конвейера ненулевым при ошибке его команды.

## Создание и сборка пустого пакета

```bash
ros2 pkg create \
  --destination-directory src \
  --build-type ament_python \
  --license Apache-2.0 \
  turtle_bringup \
  --dependencies launch launch_ros turtlesim

set -o pipefail
colcon build --symlink-install --packages-select turtle_bringup \
  2>&1 | tee evidence/pr02/build-empty.txt
```

Результат первой сборки:
`Finished <<< turtle_bringup [1.78s]`,
`Summary: 1 package finished [2.10s]`.

Пакет группирует файлы и метаданные. Сборка устанавливает его в workspace,
но сама по себе не создаёт работающую ноду.

Лог: [build-empty.txt](build-empty.txt).

## Launch-файл и итоговая сборка

В launch/sim.launch.py создана функция generate_launch_description(),
возвращающая LaunchDescription с действием Node:
package='turtlesim', executable='turtlesim_node', output='screen'.

Node из launch_ros.actions описывает запуск готового процесса.
Собственная нода с callback в этой работе не создавалась.

В setup.py добавлена установка launch/*.launch.py через data_files и glob.
package.xml содержит зависимости launch, launch_ros и turtlesim.

```bash
python3 -m py_compile src/turtle_bringup/launch/sim.launch.py
colcon build --symlink-install --packages-select turtle_bringup \
  2>&1 | tee evidence/pr02/build.txt
```

Проверка синтаксиса прошла.
Итоговая сборка:
`Finished <<< turtle_bringup [1.39s]`,
`Summary: 1 package finished [1.53s]`.

Лог: [build.txt](build.txt).

## Запуск и остановка

В терминале A подключены базовая ROS и install/setup.bash,
заданы домен 16 и rmw_fastrtps_cpp.

```bash
ros2 pkg prefix turtle_bringup
ls "$(ros2 pkg prefix turtle_bringup)/share/turtle_bringup/launch"
ros2 launch turtle_bringup sim.launch.py
```

Появилось окно turtlesim.

В отдельном терминале выполнено:

```bash
ros2 node list --no-daemon --spin-time 2
```

Во время работы launch получено `/turtlesim`.
После Ctrl+C в терминале A повторная проверка дала пустой список.

Результаты: [launch-running.txt](launch-running.txt),
[launch-stopped.txt](launch-stopped.txt).

Для следующих опытов launch запущен повторно. Teleop остановлен.

## Правильная команда: поза до и после

```bash
ros2 interface show geometry_msgs/msg/Twist
ros2 topic type /turtle1/cmd_vel
ros2 topic type /turtle1/pose
ros2 topic echo /turtle1/pose turtlesim/msg/Pose --once

ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'

sleep 2
ros2 topic echo /turtle1/pose turtlesim/msg/Pose --once
```

Ожидалось движение вперёд с поворотом против часовой стрелки.

До: x=5.544444561004639, y=5.544444561004639, theta=0.0.
После: x=6.509308815002441, y=5.796990871429443,
theta=0.5040000081062317.

Движение наблюдалось. После ожидания обе скорости стали нулевыми.
Одна публикация не поддерживает движение бесконечно:
без новых команд turtlesim останавливается.

Результаты: [pose-before.txt](pose-before.txt),
[command-once.txt](command-once.txt), [pose-after.txt](pose-after.txt).

## Сбой: неправильное полное имя

В терминале B:

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

Публикация выполнялась раз в секунду даже без подписчиков.

Пока издатель работал, в терминале C выполнено:

```bash
ros2 topic info /cmd_vel --verbose
ros2 topic info /turtle1/cmd_vel --verbose
ros2 topic echo /turtle1/pose turtlesim/msg/Pose --once
sleep 2
ros2 topic echo /turtle1/pose turtlesim/msg/Pose --once
```

| Топик | Издателей | Подписчиков |
|---|---:|---:|
| /cmd_vel | 1 | 0 |
| /turtle1/cmd_vel | 0 | 1 |

Тип обоих топиков — geometry_msgs/msg/Twist.
Подписчик правильного топика — нода turtlesim.

Две позы совпали:
x=6.509308815002441, y=5.796990871429443,
theta=0.5040000081062317.
Обе скорости равны нулю. Черепашка не двигалась.

Результаты: [wrong-topic-info.txt](wrong-topic-info.txt),
[target-topic-before-fix.txt](target-topic-before-fix.txt),
[wrong-pose-before.txt](wrong-pose-before.txt),
[wrong-pose-after.txt](wrong-pose-after.txt).

## Исправление и повторная проверка

Ошибочный издатель остановлен через Ctrl+C.
Изменено только полное имя топика: /cmd_vel на /turtle1/cmd_vel.
Тип, значения скоростей, частота, домен и RMW сохранены.

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

Пока издатель работал:

```bash
ros2 topic info /turtle1/cmd_vel --verbose
ros2 topic echo /turtle1/pose turtlesim/msg/Pose --once
```

Получены Publisher count: 1 и Subscription count: 1.
Подписчик — turtlesim.
Во время движения:
x=3.5383408069610596, y=7.457239151000977,
theta=-1.531185269355774,
linear_velocity=1.0, angular_velocity=0.5.

После Ctrl+C издателя и ожидания 2 секунд:
x=3.801224946975708, y=6.54993200302124,
theta=-1.054370641708374.
Обе скорости равны нулю.
Движение и последующая остановка наблюдались визуально.

Результаты: [fixed-topic-info.txt](fixed-topic-info.txt),
[fixed-pose-moving.txt](fixed-pose-moving.txt),
[fixed-pose-stopped.txt](fixed-pose-stopped.txt).

## Объяснение результата

/cmd_vel и /turtle1/cmd_vel — разные полные имена.
Одинаковый тип сообщения не соединяет разные топики.

Обнаружение издателя через topic info подтверждает его присутствие в графе.
Счётчик подписчиков показывает обнаруженные конечные точки.
Фактическое получение команды черепашкой подтверждено движением,
изменением Pose и ненулевыми скоростями после исправления имени.

## Источники

- Лекция 01, стр. 25: underlay, overlay и source.
- Лекция 02, стр. 2, 4, 11–18: терминал, граф, Twist, сбой имени, пакет и launch.
- Лекция 03, стр. 14: полные и относительные имена.
- ROS 2 Jazzy: [сборка colcon](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Colcon-Tutorial.html).
- ROS 2 Jazzy: [установка launch-файлов](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Launch/Launch-system.html).
- ROS 2 Jazzy: [топики и CLI](https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Topics/Understanding-ROS2-Topics.html).
