from __future__ import print_function
from six.moves import range

import os
import subprocess
import sys
from contextlib import contextmanager
import pandas as pd


def read_dict(file_name, prefix=""):
  with open(file_name, 'r') as fin:
    out_dict = {}
    for raw_elem in fin.readlines():
      if raw_elem == "":
        continue
      name, val = raw_elem.split(':', 1)
      val = val.strip()
      out_dict[prefix + name] = val
  return out_dict


def combine_results(dir_name):
  res_df = pd.DataFrame()

  dirs = os.listdir(dir_name)
  if len(dirs) == 0:
    print('No results found')
    return res_df

  for exp_name in dirs:
    params = {'dir_name': dir_name, 'exp_name': exp_name}
    file_name = os.path.join(dir_name, exp_name, 'params.log')
    params.update(read_dict(file_name))
    file_name = os.path.join(dir_name, exp_name, 'results.log')
    params.update(read_dict(file_name))
    res_df = res_df.append(params, ignore_index=True)
  return res_df


class Logger(object):
  """From stack overflow"""
  def __init__(self):
    self.terminal = sys.stdout
    bufsize = 0
    self.log = open("stdout.log", "a", bufsize)

  def write(self, message):
    self.terminal.write(message)
    self.log.write(message)

  def flush(self):
    #this flush method is needed for python 3 compatibility.
    #this handles the flush command by doing nothing.
    #you might want to specify some extra behavior here.
    self.terminal.flush()
    self.log.flush()


@contextmanager
def logging_mode(working_dir):
    """redirects stdout + changes the working dir"""
    old_dir = os.getcwd()
    os.chdir(working_dir)
    old_stdout = sys.stdout
    sys.stdout = Logger()
    try:
        yield
    finally:
        sys.stdout = old_stdout
        os.chdir(old_dir)


def get_git_hash():
  return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode()


def get_git_diff():
  return subprocess.check_output(['git', 'diff']).decode()


def get_output_folder(exp_name, parent_dir='exps', create_new=True):
  """Returns folder to save the models.

  Assumes folders in the parent_dir have suffix -run{run number}.
  Finds the highest run number and sets the output folder
  to that number + 1.

  Args:
    parent_dir: str, path of the directory containing
                all experiment runs.
    exp_name:   name of the particular experiment running
    create_new: whether to create new run or use parent_dir/exp_name
  Returns:
    parent_dir/exp_name, path to this run's save directory.
  """
  if create_new is False:
    parent_dir = os.path.join(parent_dir, exp_name)
    if not os.path.exists(parent_dir):
      os.makedirs(parent_dir)
    return parent_dir

  if not os.path.exists(parent_dir):
    os.makedirs(parent_dir)
  experiment_id = 0
  full_name = os.path.join(parent_dir, exp_name)

  for folder_name in os.listdir(parent_dir):
    cur_name = os.path.join(parent_dir, folder_name)
    if cur_name.split('-run')[0] != full_name:
      continue
    if not os.path.isdir(cur_name):
      continue
    try:
      folder_name = int(folder_name.split('-run')[-1])
      if folder_name > experiment_id:
        experiment_id = folder_name
    except:
      pass

  parent_dir = os.path.join(parent_dir, exp_name)
  parent_dir = parent_dir + '-run{}'.format(experiment_id + 1)
  if not os.path.exists(parent_dir):
    os.makedirs(parent_dir)
  return parent_dir

