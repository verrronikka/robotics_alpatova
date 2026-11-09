# ПР04. Параметризуем движение

Ubuntu 24.04.3 LTS под WSL2, ROS 2 Jazzy.
Продолжен существующий пакет patrol; пакет turtle_bringup сохранён.

## Параметры

| Параметр | По умолчанию | Допустимый диапазон |
| --- | --- | --- |
| linear_speed | 0.5 м/с | 0–1 |
| turn_rate | 0.3 рад/с | −1–1 |
| publish_hz | 10.0 Гц | 1–30 |

Значения должны быть конечными. Проверка on-set не меняет активное
состояние; post-set применяет принятые значения. При изменении частоты
старый таймер останавливается и удаляется, затем создаётся новый.
Изменение скорости не пересоздаёт таймер.

Подписка сохраняет последнюю turtlesim/msg/Pose.
До первой позы публикуется нулевой Twist; затем команда использует
принятые linear_speed и turn_rate.

## Окружение, сборка и тесты

В свежем терминале Ubuntu:

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=16
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
cd /root/robotics-inspect
colcon build --symlink-install
source install/setup.bash
colcon test --python-testing pytest --event-handlers console_direct+ \
  --return-code-on-test-failure
colcon test-result --verbose
```

Перед сборкой install/setup.bash не подключается.
В каждом дополнительном терминале нужны базовая ROS, те же переменные
окружения и /root/robotics-inspect/install/setup.bash.

## Запуск

Симулятор и patrol запускаются в отдельных терминалах:

```bash
ros2 launch turtle_bringup sim.launch.py
```

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

В третьем терминале:

```bash
ros2 param set /patrol publish_hz 5.0
ros2 param set /patrol publish_hz 0.0
ros2 param get /patrol publish_hz
ros2 topic hz /turtle1/cmd_vel
```

## Подтверждённые результаты

- Смена 10→5 Гц изменила измеренную частоту с примерно 10 до 5 Гц.
- Ноль отклонён; значение осталось 5.0, поток сохранился.
- linear_speed=0.8 и turn_rate=-0.4 появились в опубликованном Twist.
- Установка обеих скоростей в 0.0 дала нулевой Twist.
- Итог тестов: 35 проверок, 0 ошибок, 0 падений, 2 пропуска.

В ветке codex/pr04-frequency-defect, коммит
1cdbf26f801ca5dbbcd214acd57c2f04033d06d3, временно отключена проверка
частоты. Запрос нуля вызвал ZeroDivisionError при вычислении периода,
код выхода 1; patrol исчезла из графа, издателей команд стало 0.
После возврата на pr04 тот же запрос отклонён, поток около 5 Гц сохранён.

Сервис /clear вернул Empty_Response; поза неподвижной черепахи сохранилась.
Найден /turtle1/rotate_absolute типа turtlesim/action/RotateAbsolute,
сервер — /turtlesim.

Сервис возвращает один ответ на запрос. Действие имеет принятие цели,
обратную связь, итоговый результат и возможность запросить отмену.

## Материалы сдачи и CI

- [Команды, результаты и объяснения](evidence/pr04/parameters.md).
- [Результаты тестов](evidence/pr04/tests.txt).
- [Отчёт](evidence/pr04/report.json).
- [Использование ИИ](AI_USAGE.md).
- [Материалы предыдущей ПР03](evidence/pr03/demo.md).

GitHub Actions собирает оба пакета, проверяет установленный launch,
запускает тесты и checker PR04. Результат CI проверяется после push.

Course kit: v1-w10.
SHA-256: 7a91d388d7bd3def7e058c8da48c32ff27ea6f14dc880a2da169c4102d456874.

```bash
python3 .course-kit/v1/tools/check_practice.py PR04 --submission .
```

## Источники

- https://ros.lms.ci.nsu.ru/practices/pr04
- Лекция 04: стр. 3–6, 10–14, 16–17.
- https://docs.ros.org/en/jazzy/Concepts/Basic/About-Parameters.html
- https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Using-Parameters-In-A-Class-Python.html
