# ROB_2004_Final_Project

in one terminal on computer ssh into robot:
	cd team_14_andrea_and_aki/final_project /
	isb /
	ros2 launch bringup project.launch.py

in another terminal on the robot:
    ros2 run image_tools showimage --ros-args -r image:=/object_tracking/image_raw
