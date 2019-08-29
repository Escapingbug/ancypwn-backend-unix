import appdirs
import os
import signal
import docker

from ancypwn.server import ServerProcess
from ancypwn.util import _read_container_name, _make_sure_directory

from daemonize import Daemonize

APPNAME = 'ancypwn'
APPAUTHOR = 'Anciety'


TEMP_DIR = appdirs.user_cache_dir(APPNAME, APPAUTHOR)

EXIST_FLAG = os.path.join(TEMP_DIR, 'ancypwn.id')
DAEMON_PID = os.path.join(TEMP_DIR, 'ancypwn.daemon.pid')


class AlreadyRunningException(Exception):
    pass

class NotRunningException(Exception):
    pass


def _start_service(port):
    child_pid = os.fork()
    if child_pid == 0:
        def start_server():
            server = ServerProcess(port)
            server.start()
            server.join()
        daemon = Daemonize(
            app='ancypwn_terminal_server',
            pid=DAEMON_PID,
            action=start_server)
        daemon.start()


def _end_service():
    with open(DAEMON_PID, 'r') as f:
        pid = int(f.read())

    os.kill(-pid, signal.SIGTERM)
    os.remove(DAEMON_PID)


def _figure_volumes(directory):
    return {
        os.path.expanduser(directory): {
            'bind': '/pwn',
            'mod': 'rw'
        }
    }


def _attach_interactive(name, command):
    if command != '':
        cmd = 'docker exec -it {} bash -c \"{}\"'.format(
            name,
            command
        )
    else:
        cmd = 'docker exec -it {} /bin/bash'.format(name)
    os.system(cmd)


def _run_container(image_name, volumes, privileged, command):
    client = docker.from_env()
    container = client.containers
    running = container.run(
        image_name,
        '/bin/bash',
        cap_add=['SYS_ADMIN', 'SYS_PTRACE'],
        detach=True,
        tty=True,
        volumes=volumes,
        privileged=privileged,
        network_mode='host',
        remove=True
    )

    with open(EXIST_FLAG, 'w') as flag:
        flag.write(running.name)

    _attach_interactive(running.name, command)


def run(
    config=None,
    directory=None,
    image_name=None,
    priv=None,
    command=None):
    directory = os.path.abspath(directory)

    _make_sure_directory(EXIST_FLAG)
    if os.path.exists(EXIST_FLAG):
        raise AlreadyRunningException('ancypwn is already running, ' + \
            'you should either end it or attach to it')

    _start_service(config['terminal_port'])
    volumes = _figure_volumes(directory)
    try:
        _run_container(image_name, volumes, priv, command)
    except Exception as e:
        import time
        # temporary solution, to make sure service is surely started
        time.sleep(1)
        _end_service()
        raise e


def attach(config, command):
    container_name = _read_container_name(EXIST_FLAG)
    client = docker.from_env()
    container = client.containers
    conts = container.list(filters={'name': container_name})
    if len(conts) == 0:
        raise NotRunningException('ancypwn is not running, cannot attach')
    if len(conts) > 1:
        raise Exception(
            'multiple instances of image {} found'.format(image_name))

    _attach_interactive(conts[0].name, command)


def end(config):
    client = docker.from_env()
    container = client.containers
    container_name = _read_container_name(EXIST_FLAG)
    conts = container.list(filters={'name': container_name})
    if len(conts) < 1:
        os.remove(EXIST_FLAG)
        raise NotRunningException('not running')

    conts[0].stop()
    os.remove(EXIST_FLAG)
    _end_service()
