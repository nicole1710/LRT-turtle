from setuptools import find_packages, setup

package_name = 'lrt_turtle'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nicole',
    maintainer_email='nicole@todo.todo',
    description='ROS 2 node that draws LRT and author initials in turtlesim',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'pose_reader = lrt_turtle.pose_reader:main',
        ],
    },
)
