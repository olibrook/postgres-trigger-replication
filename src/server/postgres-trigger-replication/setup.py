from setuptools import setup, find_packages

setup(
    name="postgres-trigger-replication",
    version="0.0.1",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "django==1.9.1",
        "pytest==2.8.5",
        "pytest-django==2.9.1",
    ],
    entry_points={
        'console_scripts': [
        ]
    },
)
