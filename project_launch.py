from launch import LaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, ThisLaunchFileDir

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # URDF from xacro
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

    # ros2_control controller yaml
    robot_controllers = PathJoinSubstitution(
        [
            ThisLaunchFileDir(),
            "lab_3.yaml",
        ]
    )

    # -------------------------
    # Existing robot bringup
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
        output="both",
        parameters=[robot_description],
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager", "/controller_manager",
            "--controller-manager-timeout", "30"
        ],
    )

    imu_sensor_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "imu_sensor_broadcaster",
            "--controller-manager", "/controller_manager",
            "--controller-manager-timeout", "30"
        ],
    )

    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "forward_command_controller",
            "--controller-manager", "/controller_manager",
            "--controller-manager-timeout", "30"
        ],
    )

    delay_robot_controller_spawner_after_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[robot_controller_spawner],
        )
    )

    # -------------------------
    # Your custom nodes
    # -------------------------
    vision_node = Node(
        package="ball_tracker",
        executable="vision_node",
        name="vision_node",
        output="screen",
        parameters=[
            {"camera_index": 0},
            {"debug_view": True},
        ]
    )

    tracking_controller_node = Node(
        package="ball_tracker",
        executable="tracking_controller_node",
        name="tracking_controller_node",
        output="screen",
        parameters=[
            {"image_width": 640},
            {"target_x": 320.0},
            {"kp": 0.003},
            {"ki": 0.0},
            {"kd": 0.0005},
        ]
    )

    # Optional: delay custom nodes until forward_command_controller is spawned
    delay_custom_nodes_after_robot_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=robot_controller_spawner,
            on_exit=[vision_node, tracking_controller_node],
        )
    )

    nodes = [
        control_node,
        robot_state_pub_node,
        joint_state_broadcaster_spawner,
        imu_sensor_broadcaster_spawner,
        delay_robot_controller_spawner_after_joint_state_broadcaster_spawner,
        delay_custom_nodes_after_robot_controller,
    ]

    return LaunchDescription(nodes)