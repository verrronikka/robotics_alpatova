# ROS 2 graph: PR01

## 1. Рабочее состояние

Рабочий ROS 2 domain:

```text
ROS_DOMAIN_ID=16
```

В рабочем состоянии обнаруживаются два узла:

```text
/teleop_turtle
/turtlesim
```

Источник: `nodes-before.txt`.

Основные топики:

```text
/parameter_events [rcl_interfaces/msg/ParameterEvent]
/rosout [rcl_interfaces/msg/Log]
/turtle1/cmd_vel [geometry_msgs/msg/Twist]
/turtle1/color_sensor [turtlesim_msgs/msg/Color]
/turtle1/pose [turtlesim_msgs/msg/Pose]
```

Источник: `topics.txt`.

### `/turtlesim`

`/turtlesim` подписывается на:

```text
/parameter_events: rcl_interfaces/msg/ParameterEvent
/turtle1/cmd_vel: geometry_msgs/msg/Twist
```

и публикует:

```text
/parameter_events: rcl_interfaces/msg/ParameterEvent
/rosout: rcl_interfaces/msg/Log
/turtle1/color_sensor: turtlesim_msgs/msg/Color
/turtle1/pose: turtlesim_msgs/msg/Pose
```

Источник: `turtlesim-info.txt`.

### `/teleop_turtle`

`/teleop_turtle` публикует:

```text
/parameter_events: rcl_interfaces/msg/ParameterEvent
/rosout: rcl_interfaces/msg/Log
/turtle1/cmd_vel: geometry_msgs/msg/Twist
```

и имеет action client:

```text
/turtle1/rotate_absolute: turtlesim_msgs/action/RotateAbsolute
```

Источник: `teleop-info.txt`.

Основная связь:

```text
/teleop_turtle
      |
      | /turtle1/cmd_vel
      v
/turtlesim
      |
      | /turtle1/pose
      v
ROS 2 CLI / subscriber
```

Тип `/turtle1/pose`:

```text
turtlesim_msgs/msg/Pose
```

Источник: `pose-type.txt`.

## 2. Начальное состояние черепашки

До управления:

```text
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```

Источник: `pose-before.txt`.

После нажатия стрелки вверх в рабочем domain `16`:

```text
x: 7.560444355010986
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```

Координата `x` увеличилась с `5.544444561004639` до `7.560444355010986`, что подтверждает работу управления через ROS 2.

Источник: `pose-after-key-working.txt`.

## 3. Проверка частоты `/turtle1/pose`

Частота публикации `/turtle1/pose` составляет примерно `62.5 Hz`.

Измеренные значения:

```text
62.478 Hz
62.495 Hz
62.497 Hz
62.493 Hz
62.497 Hz
62.495 Hz
62.500 Hz
62.500 Hz
62.496 Hz
62.502 Hz
62.500 Hz
62.502 Hz
62.498 Hz
62.495 Hz
```

Измерение выполнялось в течение `16.135` секунд.

Источник: `pose-hz.txt`, `pose-hz-duration.txt`.

## 4. Воспроизведение дефекта

Для воспроизведения проблемы использовался другой ROS 2 domain:

```text
ROS_DOMAIN_ID=17
```

`turtlesim` продолжал работать в domain `16`.

В domain `17` обнаруживается только:

```text
/teleop_turtle
```

Источник: `nodes-broken.txt`.

Попытка получить `/turtle1/pose` в domain `17` не получает сообщения. Результат:

```text
!rclpy.ok()
```

Процесс завершается с кодом:

```text
exit=124
```

Источники: `pose-broken.txt`, `pose-broken-exit.txt`.

## 5. Проверка управления в сломанном состоянии

При нахождении управления в domain `17` нажатие стрелки вверх не изменило состояние черепашки.

Полученное состояние:

```text
x: 7.560444355010986
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```

Координата `x` осталась равной `7.560444355010986`.

Источник: `pose-after-key-broken-control.txt`.

## 6. Восстановление

После возврата в рабочий domain:

```text
ROS_DOMAIN_ID=16
```

снова обнаруживаются:

```text
/teleop_turtle
/turtlesim
```

Источник: `nodes-fixed.txt`.

Получение `/turtle1/pose` снова становится успешным:

```text
exit=0
```

Состояние черепашки:

```text
x: 9.576444625854492
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```

Источники: `pose-fixed.txt`, `pose-fixed-exit.txt`.

После повторного управления в рабочем domain:

```text
x: 11.088889122009277
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```

Источник: `pose-after-key-fixed.txt`.

## 7. Причина дефекта

Причина проблемы заключается в использовании разных ROS 2 DDS domains.

`turtlesim` работает в:

```text
ROS_DOMAIN_ID=16
```

а при воспроизведении дефекта CLI и `/teleop_turtle` использовали:

```text
ROS_DOMAIN_ID=17
```

Узлы в разных ROS 2 domains не обнаруживают друг друга и не обмениваются сообщениями.

Эксперимент подтверждает это:

```text
Domain 16:
/teleop_turtle
/turtlesim

Domain 17:
/teleop_turtle
```

В domain `17` `/turtlesim` не обнаруживается, сообщения `/turtle1/pose` не поступают, а управление не изменяет состояние симулятора.

После возврата в domain `16` обнаружение узлов и обмен сообщениями восстанавливаются.

![alt text](image-1.png)

Таким образом, дефект воспроизводится использованием разных `ROS_DOMAIN_ID` и устраняется возвратом взаимодействующих процессов в один ROS 2 domain.
