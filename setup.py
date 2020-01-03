from setuptools import setup

package_name = 'coral_enviroboard'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Richard Osterloh',
    author_email='richard.osterloh@gmail.com',
    maintainer='Richard Osterloh',
    maintainer_email='richard.osterloh@gmail.com',
    keywords=['ROS'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    description='Driver package for Environmental Sensor Board from Coral',
    license='Apache License, Version 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'enviroboard = coral_enviroboard.enviroboard:main',
        ],
    },
)