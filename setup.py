from setuptools import setup

import psychopy_tobii_infant

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='psychopy_tobii_infant',
    version=psychopy_tobii_infant.__version__,
    description='Infant-friendly eyetracking',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/yh-luo/psychopy_tobii_infant',
    author='Yu-Han Luo',
    author_email='yuhanluo1994@gmail.com',
    packages=['psychopy_tobii_infant'],
    install_requires=['tobii-research', 'PsychoPy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.5',
    zip_safe=False)
