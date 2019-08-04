from setuptools import setup, find_packages

install_requires = [
    'docker',
    'appdirs',
]

setup(
    name='ancypwn-backend-iterm2',
    version='0.0.1',
    description='ancypwn macos iterm2 backend',
    url='https://github.com/Escapingbug/ancypwn-backend-iterm2',
    author='Anciety',
    author_email='anciety@pku.edu.cn',
    packages=['ancypwn_backend_iterm2'],
    package_dir={'ancypwn_backend_iterm2': 'src'},
    install_requires=install_requires
)
