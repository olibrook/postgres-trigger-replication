from setuptools import setup, find_packages

setup(
    name="postgres-trigger-replication",
    version="0.0.1",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "django==1.9.1",
        "pytest==2.8.5",
        "pytest-django==2.9.1",
        "psycopg2==2.6.1",
        "eventlet==0.4.9",
        "pyelasticsearch==1.4",
    ],
    entry_points={
        'console_scripts': [
            'receiver=ptr.receiver:main'
        ]
    },
)
