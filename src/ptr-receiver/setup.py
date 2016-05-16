from setuptools import setup, find_packages

setup(
    name="ptr-receiver",
    version="0.0.1",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "psycopg2==2.6.1",
        "eventlet==0.19.0",
        "pyelasticsearch==1.4",
    ],
    entry_points={
        'console_scripts': [
            'receiver=ptr_receiver:main'
        ]
    },
)
