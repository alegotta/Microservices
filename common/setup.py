from setuptools import find_packages, setup

setup(
    name='apartments_common',
    version='1.0.0',
    author="pyp",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
    ],
    install_requires=[
        'flask',
        'pika',
        'python-consul'
    ],
)
