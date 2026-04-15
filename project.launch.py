from launch import LaunchDescription
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

import os


def generate_launch_description():
    # -------------------------
    # Robot description (URDF/xacro)
    # -------------------------
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [
                    FindPackageShare("pupper_v3_description"),
                    "description",
                    "pupper_v3.urdf.xacro",
                ]
            ),
        ]
    )

    robot_description = {"robot_description": robot_description_content}

    # -------------------------
    # Controller config
    # -------------------------
    robot_controllers = PathJoinSubstitution(
        [
            os.path.dirname(__file__),
            "project.yaml",   # projectct yaml
        ]
    )

    # -------------------------
    # Core robot nodes
    # -------------------------
    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, robot_controllers],
        output="both",
    )

    robot_state_pub_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[robot_description],
        output="both",
    )

    # -------------------------
    # Controller spawners
    # -------------------------
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
            "--controller-manager-timeout",
            "30",
        ],
        output="screen",
    )

    imu_sensor_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "imu_sensor_broadcaster",
            "--controller-manager",
            "/controller_manager",
            "--controller-manager-timeout",
            "30",
        ],
        output="screen",
    )

    kp_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "forward_kp_controller",
            "--controller-manager",
            "/controller_manager",
            "--controller-manager-timeout",
            "30",
        ],
        output="screen",
    )

    kd_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "forward_kd_controller",
            "--controller-manager",
            "/controller_manager",
            "--controller-manager-timeout",
            "30",
        ],
        output="screen",
    )

    # if we need gait controller / velocity controller
    # add spawner

    # -------------------------
    # Camera node
    # -------------------------
    camera_node = Node(
        package="usb_cam",              # usb_cam or package?
        executable="usb_cam_node_exe",  # our own file name
        name="camera_node",
        output="screen",
        parameters=[
            {
                "video_device": "/dev/video0",
                "image_width": 640,
                "image_height": 480,
                "framerate": 30.0,
                "pixel_format": "yuyv",
            }
        ],
    )

    # -------------------------
    # Ball detection node
    # -------------------------
    ball_detection_node = Node(
        package="your_project_package",       # change name
        executable="ball_detection_node",     # change node
        name="ball_detection_node",
        output="screen",
    )

    # -------------------------
    # Tracking / control node
    # -------------------------
    tracking_controller_node = Node(
        package="your_project_package",           # change name
        executable="tracking_controller_node",    # change node
        name="tracking_controller_node",
        output="screen",
    )

    # -------------------------
    # Visualization / debugging
    # -------------------------
    foxglove_bridge = Node(
        package="foxglove_bridge",
        executable="foxglove_bridge",
        output="both",
    )

    nodes = [
        control_node,
        robot_state_pub_node,
        joint_state_broadcaster_spawner,
        imu_sensor_broadcaster_spawner,
        kp_spawner,
        kd_spawner,
        camera_node,
        ball_detection_node,
        tracking_controller_node,
        foxglove_bridge,
    ]

    return LaunchDescription(nodes)