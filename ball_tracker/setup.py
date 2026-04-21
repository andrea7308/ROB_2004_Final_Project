from setuptools import find_packages, setup
import os 
from glob import glob

package_name = 'ball_tracker'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join("share", package_name), glob("launch/*.launch.py")),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='andrea',
    maintainer_email='ag8754@nyu.edu',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'object_detection_node = ball_tracker.object_detection:main',
            'camera_node =  ball_tracker.camera_publisher:main',
            'tracking_controller_node = ball_tracker.tracking_controller:main',
            'lab_3 = ball_tracker.lab_3:main',
        ],
    },
)
