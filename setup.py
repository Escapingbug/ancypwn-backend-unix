from setuptools import setup, find_packages

install_requires = [
    'docker',
    'appdirs',
    'daemonize',
]

setup(
    name='ancypwn-backend-unix',
    version='0.0.1',
    description='ancypwn unix universal backend',
    url='https://github.com/Escapingbug/ancypwn-backend-unix',
    author='Anciety',
    author_email='anciety@pku.edu.cn',
    packages=['ancypwn_backend_unix'],
    package_dir={'ancypwn_backend_unix': 'src'},
    install_requires=install_requires
)
