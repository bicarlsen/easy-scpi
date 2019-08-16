import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easy-scpi",
    version="0.0.4",
    author="Brian Carlsen",
    author_email="carlsen.bri@gmail.com",
    description="An easy library for controlling SCPI instruments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bicarlsen/easy-scpi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        
    ]
)