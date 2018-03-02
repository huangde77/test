from benchmark.fortune_html_parser import FortuneHTMLParser
from setup.linux import setup_util
from benchmark.test_types import *

import importlib
import os
import subprocess
import socket
import time
import re
from pprint import pprint
import sys
import traceback
import json
import logging
import csv
import shlex
import math
import multiprocessing
import docker
from collections import OrderedDict
from requests import ConnectionError
from threading import Thread
from threading import Event

from utils.output_helper import header
from utils.docker_helper import gather_docker_dependencies
from utils.docker_helper import find_docker_file

# Cross-platform colored text
from colorama import Fore, Back, Style
from datetime import datetime
from datetime import timedelta

class FrameworkTest:

  def __init__(self, name, directory, benchmarker_config, results, runTests, args):
    '''
    Constructor
    '''
    self.name = name
    self.directory = directory
    self.benchmarker_config = benchmarker_config
    self.results = results
    self.runTests = runTests
    self.fwroot = benchmarker_config.fwroot
    self.approach = ""
    self.classification = ""
    self.database = ""
    self.framework = ""
    self.language = ""
    self.orm = ""
    self.platform = ""
    self.webserver = ""
    self.os = ""
    self.database_os = ""
    self.display_name = ""
    self.notes = ""
    self.versus = ""
    self.docker_files = None

    # setup logging
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    # Used in setup.sh scripts for consistency with
    # the bash environment variables
    self.troot = self.directory

    self.__dict__.update(args)

  
  ##########################################################################################
  # Public Methods
  ##########################################################################################

  def start(self, out):
    '''
    Start the test using its setup file
    '''

    # Setup environment variables
    logDir = os.path.join(self.benchmarker_config.fwroot, self.results.directory, 'logs', self.name.lower())

    def tee_output(prefix, line):
      # Needs to be one atomic write
      # Explicitly use UTF-8 as it's the most common framework output
      # TODO improve encoding handling
      line = prefix.encode('utf-8') + line

      # Log to current terminal
      sys.stdout.write(line)
      sys.stdout.flush()

      out.write(line)
      out.flush()

    prefix = "Setup %s: " % self.name

    ###########################
    # Build the Docker images
    ##########################

    # Build the test docker file based on the test name
    # then build any additional docker files specified in the benchmark_config
    # Note - If you want to be able to stream the output of the build process you have
    # to use the low level API:
    #  https://docker-py.readthedocs.io/en/stable/api.html#module-docker.api.build

    prev_line = os.linesep
    def handle_build_output(line):
      if line.startswith('{"stream":'):
        line = json.loads(line)
        line = line[line.keys()[0]].encode('utf-8')
        if prev_line.endswith(os.linesep):
          tee_output(prefix, line)
        else:
          tee_output(line)
        self.prev_line = line

    docker_buildargs = { 'CPU_COUNT': str(multiprocessing.cpu_count()),
                         'MAX_CONCURRENCY': str(max(self.benchmarker_config.concurrency_levels)) }

    test_docker_files = ["%s.dockerfile" % self.name]
    if self.docker_files is not None:
      if type(self.docker_files) is list:
        test_docker_files.extend(self.docker_files)
      else:
        raise Exception("docker_files in benchmark_config.json must be an array")

    for test_docker_file in test_docker_files:
      deps = list(reversed(gather_docker_dependencies(os.path.join(self.directory, test_docker_file))))

      docker_dir = os.path.join(setup_util.get_fwroot(), "toolset", "setup", "linux", "docker")

      for dependency in deps:
        docker_file = os.path.join(self.directory, dependency + ".dockerfile")
        if not docker_file or not os.path.exists(docker_file):
          docker_file = find_docker_file(docker_dir, dependency + ".dockerfile")
        if not docker_file:
          tee_output(prefix, "Docker build failed; %s could not be found; terminating\n" % (dependency + ".dockerfile"))
          return 1

        # Build the dependency image
        try:
          for line in docker.APIClient(base_url='unix://var/run/docker.sock').build(
            path=os.path.dirname(docker_file),
            dockerfile="%s.dockerfile" % dependency,
            tag="tfb/%s" % dependency,
            buildargs=docker_buildargs,
            forcerm=True
          ):
            handle_build_output(line)
        except Exception as e:
          tee_output(prefix, "Docker dependency build failed; terminating\n")
          print(e)
          return 1

    # Build the test images
    for test_docker_file in test_docker_files:
      try:
        for line in docker.APIClient(base_url='unix://var/run/docker.sock').build(
          path=self.directory,
          dockerfile=test_docker_file,
          tag="tfb/test/%s" % test_docker_file.replace(".dockerfile",""),
          buildargs=docker_buildargs,
          forcerm=True
        ):
          handle_build_output(line)
      except Exception as e:
        tee_output(prefix, "Docker build failed; terminating\n")
        print(e)
        return 1


    ##########################
    # Run the Docker container
    ##########################
    client = docker.from_env()

    for test_docker_file in test_docker_files:
      try:
        def watch_container(container, prefix):
          for line in container.logs(stream=True):
            tee_output(prefix, line)

        container = client.containers.run(
          "tfb/test/%s" % test_docker_file.replace(".dockerfile", ""),
          network_mode="host",
          privileged=True,
          stderr=True,
          detach=True)

        prefix = "Server %s: " % self.name
        watch_thread = Thread(target = watch_container, args=(container,prefix))
        watch_thread.daemon = True
        watch_thread.start()

      except Exception as e:
        tee_output(prefix, "Running docker cointainer: %s failed" % test_docker_file)
        print(e)
        return 1

    return 0
    

  def verify_urls(self, logPath):
    '''
    Verifys each of the URLs for this test. THis will sinply curl the URL and 
    check for it's return status. For each url, a flag will be set on this 
    object for whether or not it passed.
    Returns True if all verifications succeeded
    '''
    result = True

    def verify_type(test_type):
      verificationPath = os.path.join(logPath, test_type)
      try:
        os.makedirs(verificationPath)
      except OSError:
        pass
      with open(os.path.join(verificationPath, 'verification.txt'), 'w') as verification:
        test = self.runTests[test_type]
        test.setup_out(verification)
        verification.write(header("VERIFYING %s" % test_type.upper()))

        base_url = "http://%s:%s" % (self.benchmarker_config.server_host, self.port)

        try:
          # Verifies headers from the server. This check is made from the
          # App Server using Pythons requests module. Will do a second check from
          # the client to make sure the server isn't only accepting connections
          # from localhost on a multi-machine setup.
          results = test.verify(base_url)

          # Now verify that the url is reachable from the client machine, unless
          # we're already failing
          if not any(result == 'fail' for (result, reason, url) in results):
            p = subprocess.call(["ssh", "TFB-client", "curl -sSf %s" % base_url + test.get_url()], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p is not 0:
              results = [('fail', "Server did not respond to request from client machine.", base_url)]
              logging.warning("""This error usually means your server is only accepting
                requests from localhost.""")
        except ConnectionError as e:
          results = [('fail',"Server did not respond to request", base_url)]
          logging.warning("Verifying test %s for %s caused an exception: %s", test_type, self.name, e)
        except Exception as e:
          results = [('fail',"""Caused Exception in TFB
            This almost certainly means your return value is incorrect,
            but also that you have found a bug. Please submit an issue
            including this message: %s\n%s""" % (e, traceback.format_exc()),
            base_url)]
          logging.warning("Verifying test %s for %s caused an exception: %s", test_type, self.name, e)
          traceback.format_exc()

        test.failed = any(result == 'fail' for (result, reason, url) in results)
        test.warned = any(result == 'warn' for (result, reason, url) in results)
        test.passed = all(result == 'pass' for (result, reason, url) in results)

        def output_result(result, reason, url):
          specific_rules_url = "http://frameworkbenchmarks.readthedocs.org/en/latest/Project-Information/Framework-Tests/#specific-test-requirements"
          color = Fore.GREEN
          if result.upper() == "WARN":
            color = Fore.YELLOW
          elif result.upper() == "FAIL":
            color = Fore.RED

          verification.write(("   " + color + "%s" + Style.RESET_ALL + " for %s\n") % (result.upper(), url))
          print("   {!s}{!s}{!s} for {!s}\n".format(color, result.upper(), Style.RESET_ALL, url))
          if reason is not None and len(reason) != 0:
            for line in reason.splitlines():
              verification.write("     " + line + '\n')
              print("     " + line)
            if not test.passed:
              verification.write("     See %s\n" % specific_rules_url)
              print("     See {!s}\n".format(specific_rules_url))

        [output_result(r1,r2,url) for (r1, r2, url) in results]

        if test.failed:
          self.results.report_verify_results(self, test_type, 'fail')
        elif test.warned:
          self.results.report_verify_results(self, test_type, 'warn')
        elif test.passed:
          self.results.report_verify_results(self, test_type, 'pass')
        else:
          raise Exception("Unknown error - test did not pass,warn,or fail")

        verification.flush()

    result = True
    for test_type in self.runTests:
      verify_type(test_type)
      if self.runTests[test_type].failed:
        result = False

    return result


  def benchmark(self, logPath):
    '''
    Runs the benchmark for each type of test that it implements
    '''
    def benchmark_type(test_type):
      benchmarkPath = os.path.join(logPath, test_type)
      try:
        os.makedirs(benchmarkPath)
      except OSError:
        pass
      with open(os.path.join(benchmarkPath, 'benchmark.txt'), 'w') as out:
        out.write("BENCHMARKING %s ... " % test_type.upper())

        test = self.runTests[test_type]
        test.setup_out(out)
        output_file = self.benchmarker.output_file(self.name, test_type)
        if not os.path.exists(output_file):
          # Open to create the empty file
          with open(output_file, 'w'):
            pass

        if not test.failed:
          if test_type == 'plaintext': # One special case
            remote_script = self.__generate_pipeline_script(test.get_url(), self.port, test.accept_header)
          elif test_type == 'query' or test_type == 'update':
            remote_script = self.__generate_query_script(test.get_url(), self.port, test.accept_header, self.benchmarker_config.query_levels)
          elif test_type == 'cached_query':
            remote_script = self.__generate_query_script(test.get_url(), self.port, test.accept_header, self.benchmarker_config.cached_query_levels)
          else:
            remote_script = self.__generate_concurrency_script(test.get_url(), self.port, test.accept_header)

          # Begin resource usage metrics collection
          self.__begin_logging(test_type)

          # Run the benchmark
          with open(output_file, 'w') as raw_file:
            p = subprocess.Popen(self.benchmarker_config.client_ssh_string.split(" "), stdin=subprocess.PIPE, stdout=raw_file, stderr=raw_file)
            p.communicate(remote_script)
            out.flush()

          # End resource usage metrics collection
          self.__end_logging()

        results = self.__parse_test(test_type)
        print("Benchmark results:")
        pprint(results)

        self.results.report_benchmark_results(framework=self, test=test_type, results=results['results'])
        out.write( "Complete\n" )
        out.flush()

    for test_type in self.runTests:
      benchmark_type(test_type)


  def parse_all(self):
    '''
    Method meant to be run for a given timestamp
    '''
    for test_type in self.runTests:
      if os.path.exists(self.benchmarker.get_output_file(self.name, test_type)):
        results = self.__parse_test(test_type)
        self.results.report_benchmark_results(framework=self, test=test_type, results=results['results'])


  def requires_database(self):
    '''Returns True/False if this test requires a database'''
    return any(tobj.requires_db for (ttype,tobj) in self.runTests.iteritems())


  ##########################################################################################
  # Private Methods
  ##########################################################################################

  def __parse_test(self, test_type):
    '''
    Parses the given test
    '''
    try:
      results = dict()
      results['results'] = []
      stats = []

      if os.path.exists(self.benchmarker.get_output_file(self.name, test_type)):
        with open(self.benchmarker.output_file(self.name, test_type)) as raw_data:
          is_warmup = True
          rawData = None
          for line in raw_data:

            if "Queries:" in line or "Concurrency:" in line:
              is_warmup = False
              rawData = None
              continue
            if "Warmup" in line or "Primer" in line:
              is_warmup = True
              continue

            if not is_warmup:
              if rawData == None:
                rawData = dict()
                results['results'].append(rawData)

              # search for weighttp data such as succeeded and failed.
              if "Latency" in line:
                m = re.findall("([0-9]+\.*[0-9]*[us|ms|s|m|%]+)", line)
                if len(m) == 4:
                  rawData['latencyAvg'] = m[0]
                  rawData['latencyStdev'] = m[1]
                  rawData['latencyMax'] = m[2]

              if "requests in" in line:
                m = re.search("([0-9]+) requests in", line)
                if m != None:
                  rawData['totalRequests'] = int(m.group(1))

              if "Socket errors" in line:
                if "connect" in line:
                  m = re.search("connect ([0-9]+)", line)
                  rawData['connect'] = int(m.group(1))
                if "read" in line:
                  m = re.search("read ([0-9]+)", line)
                  rawData['read'] = int(m.group(1))
                if "write" in line:
                  m = re.search("write ([0-9]+)", line)
                  rawData['write'] = int(m.group(1))
                if "timeout" in line:
                  m = re.search("timeout ([0-9]+)", line)
                  rawData['timeout'] = int(m.group(1))

              if "Non-2xx" in line:
                m = re.search("Non-2xx or 3xx responses: ([0-9]+)", line)
                if m != None:
                  rawData['5xx'] = int(m.group(1))
              if "STARTTIME" in line:
                m = re.search("[0-9]+", line)
                rawData["startTime"] = int(m.group(0))
              if "ENDTIME" in line:
                m = re.search("[0-9]+", line)
                rawData["endTime"] = int(m.group(0))
                test_stats = self.__parse_stats(test_type, rawData["startTime"], rawData["endTime"], 1)
                # rawData["averageStats"] = self.__calculate_average_stats(test_stats)
                stats.append(test_stats)
      with open(self.results.stats_file(self.name, test_type) + ".json", "w") as stats_file:
        json.dump(stats, stats_file, indent=2)

      return results
    except IOError:
      return None


  def __generate_concurrency_script(self, url, port, accept_header, wrk_command="wrk"):
    '''
    Generates the string containing the bash script that will be run on the 
    client to benchmark a single test. This specifically works for the variable 
    concurrency tests.
    '''
    headers = self.headers_template.format(server_host=self.benchmarker_config.server_host, accept=accept_header)
    return self.concurrency_template.format(max_concurrency=max(self.benchmarker_config.concurrency_levels),
      name=self.name, duration=self.benchmarker_config.duration,
      levels=" ".join("{}".format(item) for item in self.benchmarker_config.concurrency_levels),
      server_host=self.benchmarker_config.server_host, port=port, url=url, headers=headers, wrk=wrk_command)


  def __generate_pipeline_script(self, url, port, accept_header, wrk_command="wrk"):
    '''
    Generates the string containing the bash script that will be run on the 
    client to benchmark a single pipeline test.
    '''
    headers = self.headers_template.format(server_host=self.benchmarker_config.server_host, accept=accept_header)
    return self.pipeline_template.format(max_concurrency=max(self.benchmarker_config.pipeline_concurrency_levels),
      name=self.name, duration=self.benchmarker_config.duration,
      levels=" ".join("{}".format(item) for item in self.benchmarker_config.pipeline_concurrency_levels),
      server_host=self.benchmarker_config.server_host, port=port, url=url, headers=headers, wrk=wrk_command,
      pipeline=16)


  def __generate_query_script(self, url, port, accept_header, query_levels):
    '''
    Generates the string containing the bash script that will be run on the 
    client to benchmark a single test. This specifically works for the variable 
    query tests (Query)
    '''
    headers = self.headers_template.format(server_host=self.benchmarker_config.server_host, accept=accept_header)
    return self.query_template.format(max_concurrency=max(self.benchmarker_config.concurrency_levels),
      name=self.name, duration=self.benchmarker_config.duration,
      levels=" ".join("{}".format(item) for item in query_levels),
      server_host=self.benchmarker_config.server_host, port=port, url=url, headers=headers)


  def __begin_logging(self, test_type):
    '''
    Starts a thread to monitor the resource usage, to be synced with the 
    client's time.
    TODO: MySQL and InnoDB are possible. Figure out how to implement them.
    '''
    output_file = "{file_name}".format(file_name=self.benchmarker_config.get_stats_file(self.name, test_type))
    dstat_string = "dstat -Tafilmprs --aio --fs --ipc --lock --raw --socket --tcp \
                                      --raw --socket --tcp --udp --unix --vm --disk-util \
                                      --rpc --rpcd --output {output_file}".format(output_file=output_file)
    cmd = shlex.split(dstat_string)
    dev_null = open(os.devnull, "w")
    self.subprocess_handle = subprocess.Popen(cmd, stdout=dev_null, stderr=subprocess.STDOUT)


  def __end_logging(self):
    '''
    Stops the logger thread and blocks until shutdown is complete.
    '''
    self.subprocess_handle.terminate()
    self.subprocess_handle.communicate()


  def __parse_stats(self, test_type, start_time, end_time, interval):
    '''
    For each test type, process all the statistics, and return a multi-layered 
    dictionary that has a structure as follows:

    (timestamp)
    | (main header) - group that the stat is in
    | | (sub header) - title of the stat
    | | | (stat) - the stat itself, usually a floating point number
    '''
    stats_dict = dict()
    stats_file = self.benchmarker.stats_file(self.name, test_type)
    with open(stats_file) as stats:
      # dstat doesn't output a completely compliant CSV file - we need to strip the header
      while(stats.next() != "\n"): 
        pass
      stats_reader = csv.reader(stats)
      main_header = stats_reader.next()
      sub_header = stats_reader.next()
      time_row = sub_header.index("epoch")
      int_counter = 0
      for row in stats_reader:
        time = float(row[time_row])
        int_counter+=1
        if time < start_time:
          continue
        elif time > end_time:
          return stats_dict
        if int_counter % interval != 0:
          continue
        row_dict = dict()
        for nextheader in main_header:
          if nextheader != "":
            row_dict[nextheader] = dict()
        header = ""
        for item_num, column in enumerate(row):
          if(len(main_header[item_num]) != 0):
            header = main_header[item_num]
          # all the stats are numbers, so we want to make sure that they stay that way in json
          row_dict[header][sub_header[item_num]] = float(column) 
        stats_dict[time] = row_dict
    return stats_dict


  def __calculate_average_stats(self, raw_stats):
    '''
    We have a large amount of raw data for the statistics that may be useful 
    for the stats nerds, but most people care about a couple of numbers. For 
    now, we're only going to supply:
      * Average CPU
      * Average Memory
      * Total network use
      * Total disk use
    More may be added in the future. If they are, please update the above list.
    
    Note: raw_stats is directly from the __parse_stats method.
    
    Recall that this consists of a dictionary of timestamps, each of which 
    contain a dictionary of stat categories which contain a dictionary of stats
    '''
    raw_stat_collection = dict()

    for timestamp, time_dict in raw_stats.items():
      for main_header, sub_headers in time_dict.items():
        item_to_append = None
        if 'cpu' in main_header:
          # We want to take the idl stat and subtract it from 100
          # to get the time that the CPU is NOT idle.
          item_to_append = sub_headers['idl'] - 100.0
        elif main_header == 'memory usage':
          item_to_append = sub_headers['used']
        elif 'net' in main_header:
          # Network stats have two parts - recieve and send. We'll use a tuple of
          # style (recieve, send)
          item_to_append = (sub_headers['recv'], sub_headers['send'])
        elif 'dsk' or 'io' in main_header:
          # Similar for network, except our tuple looks like (read, write)
          item_to_append = (sub_headers['read'], sub_headers['writ'])
        if item_to_append is not None:
          if main_header not in raw_stat_collection:
            raw_stat_collection[main_header] = list()
          raw_stat_collection[main_header].append(item_to_append)

    # Simple function to determine human readable size
    # http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    def sizeof_fmt(num):
      # We'll assume that any number we get is convertable to a float, just in case
      num = float(num)
      for x in ['bytes','KB','MB','GB']:
        if num < 1024.0 and num > -1024.0:
          return "%3.1f%s" % (num, x)
        num /= 1024.0
      return "%3.1f%s" % (num, 'TB')

    # Now we have our raw stats in a readable format - we need to format it for display
    # We need a floating point sum, so the built in sum doesn't cut it
    display_stat_collection = dict()
    for header, values in raw_stat_collection.items():
      display_stat = None
      if 'cpu' in header:
        display_stat = sizeof_fmt(math.fsum(values) / len(values))
      elif main_header == 'memory usage':
        display_stat = sizeof_fmt(math.fsum(values) / len(values))
      elif 'net' in main_header:
        receive, send = zip(*values) # unzip
        display_stat = {'receive': sizeof_fmt(math.fsum(receive)), 'send': sizeof_fmt(math.fsum(send))}
      else: # if 'dsk' or 'io' in header:
        read, write = zip(*values) # unzip
        display_stat = {'read': sizeof_fmt(math.fsum(read)), 'write': sizeof_fmt(math.fsum(write))}
      display_stat_collection[header] = display_stat
    return display_stat


  ##########################################################################################
  # Constants
  ##########################################################################################
  headers_template = "-H 'Host: {server_host}' -H 'Accept: {accept}' -H 'Connection: keep-alive'"

  # Used for test types that require no pipelining or query string params.
  concurrency_template = """
    let max_threads=$(cat /proc/cpuinfo | grep processor | wc -l)
    echo ""
    echo "---------------------------------------------------------"
    echo " Running Primer {name}"
    echo " {wrk} {headers} --latency -d 5 -c 8 --timeout 8 -t 8 \"http://{server_host}:{port}{url}\""
    echo "---------------------------------------------------------"
    echo ""
    {wrk} {headers} --latency -d 5 -c 8 --timeout 8 -t 8 "http://{server_host}:{port}{url}"
    sleep 5

    echo ""
    echo "---------------------------------------------------------"
    echo " Running Warmup {name}"
    echo " {wrk} {headers} --latency -d {duration} -c {max_concurrency} --timeout 8 -t $max_threads \"http://{server_host}:{port}{url}\""
    echo "---------------------------------------------------------"
    echo ""
    {wrk} {headers} --latency -d {duration} -c {max_concurrency} --timeout 8 -t $max_threads "http://{server_host}:{port}{url}"
    sleep 5

    echo ""
    echo "---------------------------------------------------------"
    echo " Synchronizing time"
    echo "---------------------------------------------------------"
    echo ""
    ntpdate -s pool.ntp.org

    for c in {levels}
    do
      echo ""
      echo "---------------------------------------------------------"
      echo " Concurrency: $c for {name}"
      echo " {wrk} {headers} --latency -d {duration} -c $c --timeout 8 -t $(($c>$max_threads?$max_threads:$c)) \"http://{server_host}:{port}{url}\""
      echo "---------------------------------------------------------"
      echo ""
      STARTTIME=$(date +"%s")
      {wrk} {headers} --latency -d {duration} -c $c --timeout 8 -t "$(($c>$max_threads?$max_threads:$c))" http://{server_host}:{port}{url}
      echo "STARTTIME $STARTTIME"
      echo "ENDTIME $(date +"%s")"
      sleep 2
    done
  """
  # Used for test types that require pipelining.
  pipeline_template = """
    let max_threads=$(cat /proc/cpuinfo | grep processor | wc -l)
    echo ""
    echo "---------------------------------------------------------"
    echo " Running Primer {name}"
    echo " {wrk} {headers} --latency -d 5 -c 8 --timeout 8 -t 8 \"http://{server_host}:{port}{url}\""
    echo "---------------------------------------------------------"
    echo ""
    {wrk} {headers} --latency -d 5 -c 8 --timeout 8 -t 8 "http://{server_host}:{port}{url}"
    sleep 5

    echo ""
    echo "---------------------------------------------------------"
    echo " Running Warmup {name}"
    echo " {wrk} {headers} --latency -d {duration} -c {max_concurrency} --timeout 8 -t $max_threads \"http://{server_host}:{port}{url}\""
    echo "---------------------------------------------------------"
    echo ""
    {wrk} {headers} --latency -d {duration} -c {max_concurrency} --timeout 8 -t $max_threads "http://{server_host}:{port}{url}"
    sleep 5

    echo ""
    echo "---------------------------------------------------------"
    echo " Synchronizing time"
    echo "---------------------------------------------------------"
    echo ""
    ntpdate -s pool.ntp.org

    for c in {levels}
    do
      echo ""
      echo "---------------------------------------------------------"
      echo " Concurrency: $c for {name}"
      echo " {wrk} {headers} --latency -d {duration} -c $c --timeout 8 -t $(($c>$max_threads?$max_threads:$c)) \"http://{server_host}:{port}{url}\" -s ~/pipeline.lua -- {pipeline}"
      echo "---------------------------------------------------------"
      echo ""
      STARTTIME=$(date +"%s")
      {wrk} {headers} --latency -d {duration} -c $c --timeout 8 -t "$(($c>$max_threads?$max_threads:$c))" http://{server_host}:{port}{url} -s ~/pipeline.lua -- {pipeline}
      echo "STARTTIME $STARTTIME"
      echo "ENDTIME $(date +"%s")"
      sleep 2
    done
  """
  # Used for test types that require a database -
  # These tests run at a static concurrency level and vary the size of
  # the query sent with each request
  query_template = """
    let max_threads=$(cat /proc/cpuinfo | grep processor | wc -l)
    echo ""
    echo "---------------------------------------------------------"
    echo " Running Primer {name}"
    echo " wrk {headers} --latency -d 5 -c 8 --timeout 8 -t 8 \"http://{server_host}:{port}{url}2\""
    echo "---------------------------------------------------------"
    echo ""
    wrk {headers} --latency -d 5 -c 8 --timeout 8 -t 8 "http://{server_host}:{port}{url}2"
    sleep 5

    echo ""
    echo "---------------------------------------------------------"
    echo " Running Warmup {name}"
    echo " wrk {headers} --latency -d {duration} -c {max_concurrency} --timeout 8 -t $max_threads \"http://{server_host}:{port}{url}2\""
    echo "---------------------------------------------------------"
    echo ""
    wrk {headers} --latency -d {duration} -c {max_concurrency} --timeout 8 -t $max_threads "http://{server_host}:{port}{url}2"
    sleep 5

    echo ""
    echo "---------------------------------------------------------"
    echo " Synchronizing time"
    echo "---------------------------------------------------------"
    echo ""
    ntpdate -s pool.ntp.org

    for c in {levels}
    do
      echo ""
      echo "---------------------------------------------------------"
      echo " Queries: $c for {name}"
      echo " wrk {headers} --latency -d {duration} -c {max_concurrency} --timeout 8 -t $max_threads \"http://{server_host}:{port}{url}$c\""
      echo "---------------------------------------------------------"
      echo ""
      STARTTIME=$(date +"%s")
      wrk {headers} --latency -d {duration} -c {max_concurrency} --timeout 8 -t $max_threads "http://{server_host}:{port}{url}$c"
      echo "STARTTIME $STARTTIME"
      echo "ENDTIME $(date +"%s")"
      sleep 2
    done
  """


##########################################################################################
# Static Methods
##########################################################################################

def test_order(type_name):
  """
  This sort ordering is set up specifically to return the length
  of the test name. There were SO many problems involved with
  'plaintext' being run first (rather, just not last) that we
  needed to ensure that it was run last for every framework.
  """
  return len(type_name)


def validate_urls(test_name, test_keys):
  """
  Separated from validate_test because urls are not required anywhere. We know a url is incorrect if it is
  empty or does not start with a "/" character. There is no validation done to ensure the url conforms to
  the suggested url specifications, although those suggestions are presented if a url fails validation here.
  """
  example_urls = {
    "json_url":         "/json",
    "db_url":           "/mysql/db",
    "query_url":        "/mysql/queries?queries=  or  /mysql/queries/",
    "fortune_url":      "/mysql/fortunes",
    "update_url":       "/mysql/updates?queries=  or  /mysql/updates/",
    "plaintext_url":    "/plaintext",
    "cached_query_url": "/mysql/cached_queries?queries=  or /mysql/cached_queries"
  }

  for test_url in ["json_url","db_url","query_url","fortune_url","update_url","plaintext_url","cached_query_url"]:
    key_value = test_keys.get(test_url, None)
    if key_value != None and not key_value.startswith('/'):
      errmsg = """`%s` field in test \"%s\" does not appear to be a valid url: \"%s\"\n
        Example `%s` url: \"%s\"
      """ % (test_url, test_name, key_value, test_url, example_urls[test_url])
      raise Exception(errmsg)


def validate_test(test_name, test_keys, directory):
  """
  Validate benchmark config values for this test based on a schema
  """
  # Ensure that each FrameworkTest has a framework property, inheriting from top-level if not
  if not test_keys['framework']:
    test_keys['framework'] = config['framework']

  recommended_lang = directory.split('/')[-2]
  windows_url = "https://github.com/TechEmpower/FrameworkBenchmarks/issues/1038"
  schema = {
    'language': {
      'help': ('language', 'The language of the framework used, suggestion: %s' % recommended_lang)
    },
    'webserver': {
      'help': ('webserver', 'Name of the webserver also referred to as the "front-end server"')
    },
    'classification': {
      'allowed': [
        ('Fullstack', '...'),
        ('Micro', '...'),
        ('Platform', '...')
      ]
    },
    'database': {
      'allowed': [
        ('MySQL', 'One of the most popular databases around the web and in TFB'),
        ('Postgres', 'An advanced SQL database with a larger feature set than MySQL'),
        ('MongoDB', 'A popular document-store database'),
        ('Cassandra', 'A highly performant and scalable NoSQL database'),
        ('Elasticsearch', 'A distributed RESTful search engine that is used as a database for TFB tests'),
        ('Redis', 'An open-sourced, BSD licensed, advanced key-value cache and store'),
        ('SQLite', 'A network-less database, still supported for backwards compatibility'),
        ('SQLServer', 'Microsoft\'s SQL implementation'),
        ('None', 'No database was used for these tests, as is the case with Json Serialization and Plaintext')
      ]
    },
    'approach': {
      'allowed': [
        ('Realistic', '...'),
        ('Stripped', '...')
      ]
    },
    'orm': {
      'allowed': [
        ('Full', 'Has a full suite of features like lazy loading, caching, multiple language support, sometimes pre-configured with scripts.'),
        ('Micro', 'Has basic database driver capabilities such as establishing a connection and sending queries.'),
        ('Raw', 'Tests that do not use an ORM will be classified as "raw" meaning they use the platform\'s raw database connectivity.')
      ]
    },
    'platform': {
      'help': ('platform', 'Name of the platform this framework runs on, e.g. Node.js, PyPy, hhvm, JRuby ...')
    },
    'framework': {
      # Guranteed to be here and correct at this point
      # key is left here to produce the set of required keys
    },
    'os': {
      'allowed': [
        ('Linux', 'Our best-supported host OS, it is recommended that you build your tests for Linux hosts'),
        ('Windows', 'TFB is not fully-compatible on windows, contribute towards our work on compatibility: %s' % windows_url)
      ]
    },
    'database_os': {
      'allowed': [
        ('Linux', 'Our best-supported host OS, it is recommended that you build your tests for Linux hosts'),
        ('Windows', 'TFB is not fully-compatible on windows, contribute towards our work on compatibility: %s' % windows_url)
      ]
    }
  }

  # Confirm required keys are present
  required_keys = schema.keys()
  missing = list(set(required_keys) - set(test_keys))

  if len(missing) > 0:
    missingstr = (", ").join(map(str, missing))
    raise Exception("benchmark_config.json for test %s is invalid, please amend by adding the following required keys: [%s]"
      % (test_name, missingstr))

  # Check the (all optional) test urls
  validate_urls(test_name, test_keys)

  # Check values of keys against schema
  for key in required_keys:
    val = test_keys.get(key, "").lower()
    has_predefined_acceptables = 'allowed' in schema[key]

    if has_predefined_acceptables:
      allowed = schema[key].get('allowed', [])
      acceptable_values, descriptors = zip(*allowed)
      acceptable_values = [a.lower() for a in acceptable_values]

      if val not in acceptable_values:
        msg = ("Invalid `%s` value specified for test \"%s\" in framework \"%s\"; suggestions:\n"
          % (key, test_name, test_keys['framework']))
        helpinfo = ('\n').join(["  `%s` -- %s" % (v, desc) for (v, desc) in zip(acceptable_values, descriptors)])
        fullerr = msg + helpinfo + "\n"
        raise Exception(fullerr)

    elif not has_predefined_acceptables and val == "":
      msg = ("Value for `%s` in test \"%s\" in framework \"%s\" was missing:\n"
        % (key, test_name, test_keys['framework']))
      helpinfo = "  %s -- %s" % schema[key]['help']
      fullerr = msg + helpinfo + '\n'
      raise Exception(fullerr)

def parse_config(config, directory, benchmarker_config, results):
  """
  Parses a config file into a list of FrameworkTest objects
  """
  tests = []

  # The config object can specify multiple tests
  # Loop over them and parse each into a FrameworkTest
  for test in config['tests']:

    tests_to_run = [name for (name,keys) in test.iteritems()]
    if "default" not in tests_to_run:
      logging.warn("Framework %s does not define a default test in benchmark_config.json", config['framework'])

    # Check that each test configuration is acceptable
    # Throw exceptions if a field is missing, or how to improve the field
    for test_name, test_keys in test.iteritems():
      # Validates the benchmark_config entry
      validate_test(test_name, test_keys, directory)

      # Map test type to a parsed FrameworkTestType object
      runTests = dict()
      for type_name, type_obj in benchmarker_config.types.iteritems():
        try:
          # Makes a FrameWorkTestType object using some of the keys in config
          # e.g. JsonTestType uses "json_url"
          runTests[type_name] = type_obj.copy().parse(test_keys)
        except AttributeError as ae:
          # This is quite common - most tests don't support all types
          # Quitely log it and move on (debug logging is on in travis and this causes
          # ~1500 lines of debug, so I'm totally ignoring it for now
          # logging.debug("Missing arguments for test type %s for framework test %s", type_name, test_name)
          pass

      # We need to sort by test_type to run
      sortedTestKeys = sorted(runTests.keys(), key=test_order)
      sortedRunTests = OrderedDict()
      for sortedTestKey in sortedTestKeys:
        sortedRunTests[sortedTestKey] = runTests[sortedTestKey]

      # Prefix all test names with framework except 'default' test
      # Done at the end so we may still refer to the primary test as `default` in benchmark config error messages
      if test_name == 'default':
        test_name = config['framework']
      else:
        test_name = "%s-%s" % (config['framework'], test_name)

      # By passing the entire set of keys, each FrameworkTest will have a member for each key
      tests.append(FrameworkTest(test_name, directory, benchmarker_config, results, sortedRunTests, test_keys))

  return tests
