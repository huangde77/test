import os
import socket
import fnmatch
import subprocess
import multiprocessing
import json
import docker

from threading import Thread

from toolset.utils import setup_util
from toolset.utils.output_helper import tee_output
from toolset.utils.metadata_helper import gather_tests


def clean():
    '''
    Cleans all the docker images from the system
    '''
    subprocess.check_call(["docker", "image", "prune", "-f"])

    docker_ids = subprocess.check_output(["docker", "images",
                                          "-q"]).splitlines()
    for docker_id in docker_ids:
        subprocess.check_call(["docker", "image", "rmi", "-f", docker_id])

    subprocess.check_call(["docker", "system", "prune", "-a", "-f"])


def build(benchmarker_config, test_names, out):
    '''
    Builds the dependency chain as well as the test implementation docker images
    for the given tests.
    '''
    tests = gather_tests(test_names)

    for test in tests:
        docker_buildargs = {
            'CPU_COUNT': str(multiprocessing.cpu_count()),
            'MAX_CONCURRENCY': str(max(benchmarker_config.concurrency_levels)),
            'TFB_DATABASE': str(benchmarker_config.database_host)
        }

        test_docker_files = ["%s.dockerfile" % test.name]
        if test.docker_files is not None:
            if type(test.docker_files) is list:
                test_docker_files.extend(test.docker_files)
            else:
                raise Exception(
                    "docker_files in benchmark_config.json must be an array")

        for test_docker_file in test_docker_files:
            deps = list(
                reversed(
                    gather_dependencies(
                        os.path.join(test.directory, test_docker_file))))

            docker_dir = os.path.join(setup_util.get_fwroot(), "toolset",
                                      "setup", "docker")
            for dependency in deps:
                docker_file = os.path.join(test.directory,
                                           dependency + ".dockerfile")
                if not docker_file or not os.path.exists(docker_file):
                    docker_file = find(docker_dir, dependency + ".dockerfile")
                if not docker_file:
                    tee_output(
                        out,
                        "Docker build failed; %s could not be found; terminating\n"
                        % (dependency + ".dockerfile"))
                    return 1

                # Build the dependency image
                try:
                    for line in docker.APIClient(
                            base_url='unix://var/run/docker.sock').build(
                                path=os.path.dirname(docker_file),
                                dockerfile="%s.dockerfile" % dependency,
                                tag="tfb/%s" % dependency,
                                buildargs=docker_buildargs,
                                forcerm=True):
                        prev_line = os.linesep
                        if line.startswith('{"stream":'):
                            line = json.loads(line)
                            line = line[line.keys()[0]].encode('utf-8')
                            if prev_line.endswith(os.linesep):
                                tee_output(out, line)
                            else:
                                tee_output(out, line)
                            prev_line = line
                except Exception as e:
                    tee_output(out,
                               "Docker dependency build failed; terminating\n")
                    print(e)
                    return 1

        # Build the test images
        for test_docker_file in test_docker_files:
            print(test)
            try:
                for line in docker.APIClient(
                        base_url='unix://var/run/docker.sock').build(
                            path=test.directory,
                            dockerfile=test_docker_file,
                            tag="tfb/test/%s" % test_docker_file.replace(
                                ".dockerfile", ""),
                            buildargs=docker_buildargs,
                            forcerm=True):
                    prev_line = os.linesep
                    if line.startswith('{"stream":'):
                        line = json.loads(line)
                        line = line[line.keys()[0]].encode('utf-8')
                        if prev_line.endswith(os.linesep):
                            tee_output(out, line)
                        else:
                            tee_output(out, line)
                        prev_line = line
            except Exception as e:
                tee_output(out, "Docker build failed; terminating\n")
                print(e)
                return 1


def run(benchmarker_config, docker_files, out):
    '''
    Run the given Docker container(s)
    '''
    client = docker.from_env()

    for docker_file in docker_files:
        try:

            def watch_container(container):
                for line in container.logs(stream=True):
                    tee_output(out, line)

            extra_hosts = {
                socket.gethostname(): str(benchmarker_config.server_host),
                'TFB-SERVER': str(benchmarker_config.server_host),
                'TFB-DATABASE': str(benchmarker_config.database_host),
                'TFB-CLIENT': str(benchmarker_config.client_host)
            }

            print(extra_hosts)

            container = client.containers.run(
                "tfb/test/%s" % docker_file.replace(".dockerfile", ""),
                network_mode="host",
                privileged=True,
                stderr=True,
                detach=True,
                extra_hosts=extra_hosts)

            watch_thread = Thread(target=watch_container, args=(container, ))
            watch_thread.daemon = True
            watch_thread.start()

        except Exception as e:
            tee_output(out,
                       "Running docker cointainer: %s failed" % docker_file)
            print(e)
            return 1


def find(path, pattern):
    '''
    Finds and returns all the the files matching the given pattern recursively in
    the given path. 
    '''
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                return os.path.join(root, name)


def gather_dependencies(docker_file):
    '''
    Gathers all the known docker dependencies for the given docker image.
    '''
    # Avoid setting up a circular import
    from toolset.utils import setup_util
    deps = []

    docker_dir = os.path.join(setup_util.get_fwroot(), "toolset", "setup",
                              "docker")

    if os.path.exists(docker_file):
        with open(docker_file) as fp:
            for line in fp.readlines():
                tokens = line.strip().split(' ')
                if tokens[0] == "FROM":
                    # This is magic that our base image points to
                    if tokens[1] != "ubuntu:16.04":
                        depToken = tokens[1].strip().split(':')[
                            0].strip().split('/')[1]
                        deps.append(depToken)
                        dep_docker_file = os.path.join(
                            os.path.dirname(docker_file),
                            depToken + ".dockerfile")
                        if not os.path.exists(dep_docker_file):
                            dep_docker_file = find(docker_dir,
                                                   depToken + ".dockerfile")
                        deps.extend(gather_dependencies(dep_docker_file))

    return deps
