# Copyright 2024 YOLOs-CPP Team
# SPDX-License-Identifier: AGPL-3.0

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import LifecycleNode, LifecycleTransition
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
from lifecycle_msgs.msg import Transition


def generate_launch_description():
    """Launch YOLO segmentor node as composable lifecycle node."""
    default_params = PathJoinSubstitution(
        [FindPackageShare("ros2_yolos_cpp"), "config", "default_params.yaml"]
    )

    # Declare launch arguments
    model_path_arg = DeclareLaunchArgument(
        "model_path", description="Path to ONNX model file"
    )
    labels_path_arg = DeclareLaunchArgument(
        "labels_path", description="Path to class names file"
    )
    use_gpu_arg = DeclareLaunchArgument(
        "use_gpu", default_value="false", description="Enable GPU inference"
    )
    conf_threshold_arg = DeclareLaunchArgument(
        "conf_threshold", default_value="0.4", description="Confidence threshold"
    )
    nms_threshold_arg = DeclareLaunchArgument(
        "nms_threshold", default_value="0.45", description="NMS threshold"
    )
    image_topic_arg = DeclareLaunchArgument(
        "image_topic",
        default_value="/camera/image_raw",
        description="Input image topic",
    )
    auto_start_arg = DeclareLaunchArgument(
        "auto_start",
        default_value="true",
        description="Automatically configure and activate the lifecycle segmentor node",
    )
    lifecycle_start_delay_arg = DeclareLaunchArgument(
        "lifecycle_start_delay",
        default_value="0.5",
        description="Seconds to wait before triggering lifecycle configure/activate",
    )

    segmentor_node = LifecycleNode(
        package="ros2_yolos_cpp",
        executable="yolos_segmentor_node",
        name="yolos_segmentor",
        namespace="",
        parameters=[
            default_params,
            {
                "model_path": LaunchConfiguration("model_path"),
                "labels_path": LaunchConfiguration("labels_path"),
                "use_gpu": ParameterValue(
                    LaunchConfiguration("use_gpu"), value_type=bool
                ),
                "conf_threshold": ParameterValue(
                    LaunchConfiguration("conf_threshold"), value_type=float
                ),
                "nms_threshold": ParameterValue(
                    LaunchConfiguration("nms_threshold"), value_type=float
                ),
                "publish_debug_image": True,
            }
        ],
        remappings=[
            ("~/image_raw", LaunchConfiguration("image_topic")),
        ],
        output="screen",
    )

    lifecycle_start = TimerAction(
        period=LaunchConfiguration("lifecycle_start_delay"),
        actions=[
            LifecycleTransition(
                lifecycle_node_names=["/yolos_segmentor"],
                transition_ids=[
                    Transition.TRANSITION_CONFIGURE,
                    Transition.TRANSITION_ACTIVATE,
                ],
                condition=IfCondition(LaunchConfiguration("auto_start")),
            )
        ],
    )

    return LaunchDescription(
        [
            model_path_arg,
            labels_path_arg,
            use_gpu_arg,
            conf_threshold_arg,
            nms_threshold_arg,
            image_topic_arg,
            auto_start_arg,
            lifecycle_start_delay_arg,
            segmentor_node,
            lifecycle_start,
        ]
    )
