from setuptools import setup, find_packages

setup(
    name="ptr-web",
    version="0.0.1",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "django==1.9.1",
        "psycopg2==2.6.1",
    ]
)
