from setuptools import setup, find_packages

setup(
    name="ptr-integration",
    version="0.0.1",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "pytest==2.8.5",
        "pytest-django==2.9.1",
        "ptr-web",
        "ptr-receiver",
    ]
)
