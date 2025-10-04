from setuptools import find_packages, setup

package_name = 'task_main'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='song',
    maintainer_email='song@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'set_mode_client = task_main.set_mode_client:main',
            'minimal_publisher = task_main.minimal_publisher:main',
            'minimal_subscriber = task_main.minimal_subscriber:main',
        ],
    },
)
