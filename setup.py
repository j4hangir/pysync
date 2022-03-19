from setuptools import setup

setup(name='pysync',
      version='1.1.0',
      description='Multithreaded rsync in Python',
      url='https://git.j4hangir.com/py/pysync.git',
      author='j4hangir',
      author_email='j4hangir@icloud.com',
      packages=['pysync'],
      scripts=['bin/pysync'],
      install_requires=[
          'tqdm',
      ],
      zip_safe=False)
