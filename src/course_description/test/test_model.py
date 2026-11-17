"""Check the frame tree and sensor mounts against the reference SDF."""

from pathlib import Path
import xml.etree.ElementTree as ET

import pytest
import xacro


@pytest.fixture(scope='module')
def robot():
    model = Path(__file__).resolve().parents[1] / 'urdf' / 'vehicle.urdf.xacro'
    return ET.fromstring(xacro.process_file(str(model)).toxml())


def test_tree(robot):
    names = [link.attrib['name'] for link in robot.findall('link')]
    links = set(names)
    assert len(names) == len(links), 'Duplicate link names'

    parents = {}
    joint_names = set()
    for joint in robot.findall('joint'):
        name = joint.attrib['name']
        assert name not in joint_names, f'Duplicate joint: {name}'
        joint_names.add(name)

        parent = joint.find('parent').attrib['link']
        child = joint.find('child').attrib['link']
        assert parent in links, f'Unknown parent: {parent}'
        assert child in links, f'Unknown child: {child}'
        assert child not in parents, f'Multiple parents for {child}'
        parents[child] = parent

    assert links - set(parents) == {'base_link'}

    for frame in links:
        seen = set()
        while frame in parents:
            assert frame not in seen, f'Cycle involving {frame}'
            seen.add(frame)
            frame = parents[frame]
        assert frame == 'base_link'


@pytest.mark.parametrize('sensor', ['camera_link', 'lidar_link', 'imu_link'])
def test_sensor_mounts(robot, sensor):
    matches = [
        joint for joint in robot.findall('joint')
        if joint.find('child').attrib['link'] == sensor
    ]
    assert len(matches) == 1, f'Expected one joint for {sensor}'
    joint = matches[0]

    assert joint.attrib['type'] == 'fixed'
    assert joint.find('parent').attrib['link'] == 'base_link', (
        f'{sensor} must be attached directly to base_link'
    )

    origin = joint.find('origin')
    xyz = tuple(map(float, origin.attrib['xyz'].split()))
    rpy = tuple(map(float, origin.attrib['rpy'].split()))
    assert xyz == pytest.approx((0.28, 0.0, 0.38))
    assert rpy == pytest.approx((0.0, 0.0, 0.0))


@pytest.mark.parametrize('joint_name,expected', [
    ('front_left_steering_joint', (0.40, 0.31, 0.0)),
    ('front_right_steering_joint', (0.40, -0.31, 0.0)),
    ('rear_left_wheel_joint', (-0.40, 0.31, 0.0)),
    ('rear_right_wheel_joint', (-0.40, -0.31, 0.0)),
])
def test_axle_positions(robot, joint_name, expected):
    joint = robot.find(f"./joint[@name='{joint_name}']")
    assert joint is not None, f'Missing joint: {joint_name}'
    assert joint.find('parent').attrib['link'] == 'base_link'
    xyz = tuple(map(float, joint.find('origin').attrib['xyz'].split()))
    assert xyz == pytest.approx(expected)


@pytest.mark.parametrize('wheel,parent', [
    ('front_left_wheel', 'front_left_knuckle'),
    ('front_right_wheel', 'front_right_knuckle'),
    ('rear_left_wheel', 'base_link'),
    ('rear_right_wheel', 'base_link'),
])
def test_wheel_geometry(robot, wheel, parent):
    from math import pi

    link = robot.find(f"./link[@name='{wheel}']")
    assert link is not None, f'Missing wheel: {wheel}'
    for role in ('visual', 'collision'):
        shape = link.find(role)
        assert shape is not None, f'{wheel}: missing {role}'
        cylinder = shape.find('geometry/cylinder')
        assert cylinder is not None
        assert float(cylinder.attrib['radius']) == pytest.approx(0.12)
        assert float(cylinder.attrib['length']) == pytest.approx(0.07)
        rpy = tuple(map(float, shape.find('origin').attrib['rpy'].split()))
        assert rpy == pytest.approx((pi / 2, 0.0, 0.0))

    joint = robot.find(f"./joint[@name='{wheel}_joint']")
    assert joint is not None
    assert joint.attrib['type'] == 'continuous'
    assert joint.find('parent').attrib['link'] == parent
    axis = tuple(map(float, joint.find('axis').attrib['xyz'].split()))
    assert axis == pytest.approx((0.0, 1.0, 0.0))
    if parent != 'base_link':
        xyz = tuple(map(float, joint.find('origin').attrib['xyz'].split()))
        assert xyz == pytest.approx((0.0, 0.0, 0.0))


def test_inertial_numbers(robot):
    from math import isfinite

    inertials = robot.findall('./link/inertial')
    assert inertials, 'No inertial data found'
    for inertial in inertials:
        mass = float(inertial.find('mass').attrib['value'])
        assert isfinite(mass) and mass > 0
        tensor = inertial.find('inertia').attrib
        for key in ('ixx', 'iyy', 'izz', 'ixy', 'ixz', 'iyz'):
            assert isfinite(float(tensor[key])), f'Non-finite {key}'
        for key in ('ixx', 'iyy', 'izz'):
            assert float(tensor[key]) > 0, f'Non-positive {key}'
