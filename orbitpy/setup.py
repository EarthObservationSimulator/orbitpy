from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='OrbitPy',
    version='0.1',
    description='Orbit Module',
    author='BAERI',
    author_email='vinay.ravindra@nasa.gov',
    packages=['orbitpy'],
    scripts=[ # TODO: remove this? Does not seem to serve any purpose. 
    'bin/run_mission.py'
    ],
    install_requires=['numpy'] 
)
