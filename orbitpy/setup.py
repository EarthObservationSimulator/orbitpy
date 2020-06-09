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
    install_requires=['numpy', 'instrupy', 'nose', 'pandas', 'scipy', 'sphinx', 
                      'sphinx_rtd_theme'] # Install also requires sphinxcontrib.plantuml, sphinxcontrib.needs which are commanded to
                                          # to be installed separately in the Makefile in non-editable mode (without the '-e' flag). 
                                          # Reason: Bug exists when installed in editable mode (the mode under which OrbitPy is installed)
)
