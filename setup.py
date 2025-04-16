from setuptools import setup, find_packages

setup(
    name="ourchants-api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "marshmallow==3.21.0",
        "boto3>=1.9.201",
        "pytest==8.1.1",
        "pytest-cov==4.1.0",
        "moto[dynamodb]==5.0.3",
        "requests==2.31.0",
        "coverage==7.4.4",
        "pytest-watch==4.2.0",
    ],
) 