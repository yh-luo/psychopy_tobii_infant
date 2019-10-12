import psychopy_tobii_infant
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='psychopy_tobii_infant',
      version=psychopy_tobii_infant.__version__,
      description='Infant-friendly eyetracking',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/yh-luo/psychopy_tobii_infant',
      author='Yu-Han Luo',
      author_email='yuhanluo1994@gmail.com',
      license='GPL v3.0 or later',
      packages=['psychopy_tobii_infant'],
      install_requires=['tobii-research', 'PsychoPy'],
      zip_safe=False)
