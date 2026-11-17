# PR06: системы координат и владельцы преобразований

## Реализация

- Итоговый коммит реализации: ef2d0c3ddf47f03bb52b185068933abc233f5edc.
- Коммит модели и тестов: 06ca6dabae0144e278f429e815d0f9f26d8dfeb6.
- Последующий коммит изменяет только проверку PR05 в CI.
- Источник размеров: course kit v1-w11, models/course_ackermann/model.sdf.
- База: 0.8 м; колея: 0.62 м; радиус колеса: 0.12 м; ширина: 0.07 м.
- Единицы: метры, килограммы, секунды, радианы.
- Оси звеньев: X вперёд, Y влево, Z вверх, согласно REP-103.

## Фиксированные связи

XYZ задаёт положение дочернего звена относительно родительского.
У всех перечисленных фиксированных связей RPY=(0, 0, 0).

| Родитель | Потомок | XYZ, м | Канал | Владелец |
| --- | --- | --- | --- | --- |
| base_link | camera_link | (0.28, 0, 0.38) | /tf_static | /robot_state_publisher |
| base_link | lidar_link | (0.28, 0, 0.38) | /tf_static | /robot_state_publisher |
| base_link | imu_link | (0.28, 0, 0.38) | /tf_static | /robot_state_publisher |

Одинаковые положения трёх сенсоров сохранены из исходного SDF.
Смещение visual/collision корпуса по Z=0.12 м не меняет начало base_link.

## Подвижные связи

q обозначает положение соответствующего шарнира из /joint_states.
Rz(q) — вращение вокруг Z, Ry(q) — вокруг Y; при q=0 поворот нулевой.

| Родитель | Потомок | XYZ, м | Поворот | Канал | Владелец |
| --- | --- | --- | --- | --- | --- |
| base_link | front_left_knuckle | (0.40, 0.31, 0) | Rz(q) | /tf | /robot_state_publisher |
| base_link | front_right_knuckle | (0.40, -0.31, 0) | Rz(q) | /tf | /robot_state_publisher |
| front_left_knuckle | front_left_wheel | (0, 0, 0) | Ry(q) | /tf | /robot_state_publisher |
| front_right_knuckle | front_right_wheel | (0, 0, 0) | Ry(q) | /tf | /robot_state_publisher |
| base_link | rear_left_wheel | (-0.40, 0.31, 0) | Ry(q) | /tf | /robot_state_publisher |
| base_link | rear_right_wheel | (-0.40, -0.31, 0) | Ry(q) | /tf | /robot_state_publisher |

Поворот цилиндров visual/collision на pi/2 вокруг X задаёт форму колёс;
он не поворачивает систему координат самого wheel link.
Пределы рулевых шарниров: [-0.55, 0.55] рад.
Вращение колёс задаётся continuous-шарнирами.

Публикация /joint_states подаёт значения шарниров;
владельцем преобразований остаётся robot_state_publisher.
Модель открыта в RViz с шестью нулевыми положениями шарниров,
Global Status: Ok.
Финальные view_frames до и после исправления снимались без
публикации /joint_states и показывают фиксированные сенсоры.

## Дефект и исправление

Ветка: codex/pr06-lidar-parent-defect.
Коммит дефекта: 5eefe31dff7babdd8fd73adf619b35b65de103e2.

При замене родителя лидара на camera_link с прежним offset:
- check_urdf принял дерево, exit=0;
- test_sensor_mounts[lidar_link] упал: 1 failed, 12 passed, exit=1;
- tf2_echo показал base_link -> lidar_link: (0.56, 0, 0.76) м;
- view_frames показал цепочку base_link -> camera_link -> lidar_link.

После возврата в pr06:
- check_urdf прошёл, exit=0;
- те же 13 тестов прошли, exit=0;
- tf2_echo показал (0.28, 0, 0.38) м;
- view_frames показал прямую связь base_link -> lidar_link.

Логи: defect-before.txt, defect-after.txt, tf-before.txt, tf-after.txt,
frames-before.txt, frames-after.txt.
Графы сохранены в каталогах tf-before/ и tf-after/.
