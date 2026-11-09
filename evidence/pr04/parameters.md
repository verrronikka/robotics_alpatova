# ПР04. Параметры: команды и результаты

Коммит реализации: `f197bd4a9052de534dcccc95da6f205e3e7c7bdf`.

Окружение: Ubuntu 24.04.3 под WSL2, ROS 2 Jazzy; ROS_DOMAIN_ID=16, RMW_IMPLEMENTATION=rmw_fastrtps_cpp.

Симулятор: `ros2 launch turtle_bringup sim.launch.py`. Patrol запускалась с remap `cmd_vel:=/turtle1/cmd_vel`.

Допустимы конечные значения: publish_hz 1–30, linear_speed 0–1, turn_rate −1–1. on-set проверяет вход без изменения состояния; post-set применяет принятые значения и при смене частоты останавливает и удаляет старый таймер перед созданием нового.

Дефект воспроизведён в ветке `codex/pr04-frequency-defect`. После запроса нуля возник ZeroDivisionError при вычислении периода; код выхода patrol — 1. После восстановления проверки ноль отклонён, значение 5.0 и поток около 5 Гц сохранены.

Логи ниже получены из реальных пользовательских запусков. Перенаправление через tee показано сохранёнными именами файлов. Измерения hz ограничивались 10 секундами.

## Исходная частота

```bash
ros2 param get /patrol publish_hz
```

Лог: `parameter-before.txt`.

```text
Double value is: 10.0
```

```bash
PYTHONUNBUFFERED=1 timeout --signal=INT --kill-after=3s 10s ros2 topic hz /turtle1/cmd_vel --window 20
```

Лог: `hz-10.txt`.

```text
average rate: 9.993
	min: 0.098s max: 0.101s std dev: 0.00072s window: 11
average rate: 10.004
	min: 0.098s max: 0.101s std dev: 0.00060s window: 20
average rate: 9.998
	min: 0.099s max: 0.101s std dev: 0.00037s window: 20
average rate: 9.997
	min: 0.100s max: 0.100s std dev: 0.00029s window: 20
average rate: 10.002
	min: 0.099s max: 0.101s std dev: 0.00042s window: 20
average rate: 10.000
	min: 0.099s max: 0.101s std dev: 0.00065s window: 20
```

## Изменение 10→5 Гц

```bash
ros2 param set /patrol publish_hz 5.0
```

Лог: `set-5.txt`.

```text
Set parameter successful
```

```bash
ros2 param get /patrol publish_hz
```

Лог: `parameter-5.txt`.

```text
Double value is: 5.0
```

```bash
PYTHONUNBUFFERED=1 timeout --signal=INT --kill-after=3s 10s ros2 topic hz /turtle1/cmd_vel --window 20
```

Лог: `hz-5.txt`.

```text
average rate: 4.999
	min: 0.199s max: 0.202s std dev: 0.00119s window: 6
average rate: 5.003
	min: 0.198s max: 0.202s std dev: 0.00112s window: 12
average rate: 5.000
	min: 0.198s max: 0.202s std dev: 0.00097s window: 17
average rate: 5.000
	min: 0.198s max: 0.202s std dev: 0.00098s window: 20
average rate: 5.001
	min: 0.198s max: 0.202s std dev: 0.00089s window: 20
average rate: 4.999
	min: 0.199s max: 0.202s std dev: 0.00084s window: 20
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00084s window: 20
```

## Отклонение нуля

```bash
ros2 param set /patrol publish_hz 0.0
```

Лог: `reject-zero.txt`.

```text
Setting parameter failed: publish_hz must be in [1.0, 30.0]
```

```bash
ros2 param get /patrol publish_hz
```

Лог: `parameter-after-zero.txt`.

```text
Double value is: 5.0
```

```bash
PYTHONUNBUFFERED=1 timeout --signal=INT --kill-after=3s 10s ros2 topic hz /turtle1/cmd_vel --window 20
```

Лог: `hz-after-zero.txt`.

```text
average rate: 4.996
	min: 0.199s max: 0.201s std dev: 0.00076s window: 7
average rate: 4.998
	min: 0.199s max: 0.201s std dev: 0.00073s window: 13
average rate: 4.999
	min: 0.199s max: 0.201s std dev: 0.00076s window: 19
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00081s window: 20
average rate: 5.001
	min: 0.199s max: 0.201s std dev: 0.00074s window: 20
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00077s window: 20
average rate: 5.000
	min: 0.198s max: 0.201s std dev: 0.00082s window: 20
```

## Дефект: проверка частоты отключена в отдельной ветке

```bash
git rev-parse HEAD
```

Лог: `defect-commit.txt`.

```text
1cdbf26f801ca5dbbcd214acd57c2f04033d06d3
```

```bash
ros2 param set /patrol publish_hz 5.0
```

Лог: `broken-set-5.txt`.

```text
Set parameter successful
```

```bash
PYTHONUNBUFFERED=1 timeout --signal=INT --kill-after=3s 10s ros2 param set /patrol publish_hz 0.0
```

Лог: `broken-set-zero.txt`.

```text
(пустой вывод)
```

```bash
PYTHONUNBUFFERED=1 ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Лог: `patrol-broken.txt`.

```text
Traceback (most recent call last):
  File "/root/robotics-inspect/install/patrol/lib/patrol/patrol", line 33, in <module>
    sys.exit(load_entry_point('patrol', 'console_scripts', 'patrol')())
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/robotics-inspect/build/patrol/patrol/patrol.py", line 96, in main
    rclpy.spin(node)
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/__init__.py", line 247, in spin
    executor.spin_once()
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/executors.py", line 926, in spin_once
    self._spin_once_impl(timeout_sec)
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/executors.py", line 918, in _spin_once_impl
    raise handler.exception()
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/task.py", line 286, in _execute_coroutine_step
    result = coro.send(None)
             ^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/executors.py", line 592, in handler
    await call_coroutine()
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/executors.py", line 531, in _execute
    response = await await_or_execute(srv.callback, request, srv.srv_type.Response())
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/executors.py", line 115, in await_or_execute
    return callback(*args)
           ^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/parameter_service.py", line 117, in _set_parameters_callback
    result = node.set_parameters_atomically([param])
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/node.py", line 839, in set_parameters_atomically
    return self._set_parameters_atomically(parameter_list)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/node.py", line 859, in _set_parameters_atomically
    return self._set_parameters_atomically_common(parameter_list)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/node.py", line 962, in _set_parameters_atomically_common
    self._call_post_set_parameters_callback(parameter_list)
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/node.py", line 1055, in _call_post_set_parameters_callback
    callback(parameter_list)
  File "/root/robotics-inspect/build/patrol/patrol/patrol.py", line 75, in apply_parameters
    1.0 / self.publish_hz, self.on_timer,
    ~~~~^~~~~~~~~~~~~~~~~
ZeroDivisionError: float division by zero
[ros2run]: Process exited with failure 1
```

```bash
ros2 node list
```

Лог: `broken-nodes.txt`.

```text
/turtlesim
```

```bash
ros2 topic info /turtle1/cmd_vel --verbose
```

Лог: `broken-endpoints.txt`.

```text
Type: geometry_msgs/msg/Twist

Publisher count: 0

Subscription count: 1

Node name: turtlesim
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: SUBSCRIPTION
GID: 01.0f.51.42.77.0a.a7.d5.00.00.00.00.00.00.1d.04
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite
```

## Повторение после возврата в pr04

```bash
ros2 param set /patrol publish_hz 5.0
```

Лог: `restored-set-5.txt`.

```text
Set parameter successful
```

```bash
PYTHONUNBUFFERED=1 timeout --signal=INT --kill-after=3s 10s ros2 param set /patrol publish_hz 0.0
```

Лог: `restored-reject-zero.txt`.

```text
Setting parameter failed: publish_hz must be in [1.0, 30.0]
```

```bash
ros2 param get /patrol publish_hz
```

Лог: `restored-parameter.txt`.

```text
Double value is: 5.0
```

```bash
PYTHONUNBUFFERED=1 timeout --signal=INT --kill-after=3s 10s ros2 topic hz /turtle1/cmd_vel --window 20
```

Лог: `restored-hz.txt`.

```text
WARNING: topic [/turtle1/cmd_vel] does not appear to be published yet
average rate: 5.002
	min: 0.199s max: 0.201s std dev: 0.00067s window: 7
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00076s window: 12
average rate: 4.999
	min: 0.199s max: 0.201s std dev: 0.00076s window: 17
average rate: 4.999
	min: 0.198s max: 0.202s std dev: 0.00087s window: 20
average rate: 5.000
	min: 0.198s max: 0.203s std dev: 0.00110s window: 20
average rate: 5.000
	min: 0.198s max: 0.203s std dev: 0.00112s window: 20
```

```bash
ros2 node list
```

Лог: `restored-nodes.txt`.

```text
/patrol
/turtlesim
```

## Изменение скоростей

```bash
ros2 param set /patrol linear_speed 0.8
```

Лог: `set-linear-speed.txt`.

```text
Set parameter successful
```

```bash
ros2 param set /patrol turn_rate -0.4
```

Лог: `set-turn-rate.txt`.

```text
Set parameter successful
```

```bash
ros2 topic echo /turtle1/cmd_vel --once
```

Лог: `configured-command.txt`.

```text
linear:
  x: 0.8
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: -0.4
---
```

## Остановка параметрами

```bash
ros2 param set /patrol linear_speed 0.0
```

Лог: `stop-linear.txt`.

```text
Set parameter successful
```

```bash
ros2 param set /patrol turn_rate 0.0
```

Лог: `stop-turn.txt`.

```text
Set parameter successful
```

```bash
ros2 topic echo /turtle1/cmd_vel --once
```

Лог: `stopped-command.txt`.

```text
linear:
  x: 0.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0
---
```

## Готовый сервис /clear

```bash
ros2 service type /clear
```

Лог: `clear-type.txt`.

```text
std_srvs/srv/Empty
```

```bash
ros2 topic echo /turtle1/pose --once
```

Лог: `pose-before-clear.txt`.

```text
x: 11.063323020935059
y: 7.457615852355957
theta: -2.214061975479126
linear_velocity: 0.0
angular_velocity: 0.0
---
```

```bash
ros2 service call /clear std_srvs/srv/Empty '{}'
```

Лог: `clear-call.txt`.

```text
waiting for service to become available...
requester: making request: std_srvs.srv.Empty_Request()

response:
std_srvs.srv.Empty_Response()
```

```bash
ros2 topic echo /turtle1/pose --once
```

Лог: `pose-after-clear.txt`.

```text
x: 11.063323020935059
y: 7.457615852355957
theta: -2.214061975479126
linear_velocity: 0.0
angular_velocity: 0.0
---
```

## Готовое действие поворота

```bash
ros2 action list -t
```

Лог: `actions.txt`.

```text
/turtle1/rotate_absolute [turtlesim/action/RotateAbsolute]
```

```bash
ros2 action info /turtle1/rotate_absolute
```

Лог: `rotate-action-info.txt`.

```text
Action: /turtle1/rotate_absolute
Action clients: 0
Action servers: 1
    /turtlesim
```

## Сервис и действие

Запрос сервиса /clear получает один ответ о завершении операции. Цель действия rotate_absolute имеет отдельное принятие, обратную связь, итоговый результат и возможность запросить отмену.

Ответ /clear получен; координаты, угол и нулевые скорости до и после вызова совпали. Найдено действие turtlesim/action/RotateAbsolute с одним сервером /turtlesim.

## Тесты

Результаты: [tests.txt](tests.txt); подробный прогон: [colcon-test.txt](colcon-test.txt). Итог: 35 тестов, 0 ошибок, 0 падений, 2 пропуска.

## Источники

- https://ros.lms.ci.nsu.ru/practices/pr04
- Лекция 04, стр. 3–6, 10–14, 16–17.
- https://docs.ros.org/en/jazzy/Concepts/Basic/About-Parameters.html
