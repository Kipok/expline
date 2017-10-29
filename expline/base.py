import os
import argparse
from utils import get_output_folder, get_git_hash, \
                  get_git_diff, logging_mode

# TODO(@igor): maybe add some load_model helper functionality?
# TODO(@igor): add script to parse experiments folder and 
#              return a convenient csv table

class BaseExperiment(object):
  """Base experiment class for the unified experiments pipeline.
  This is the class, that you should inherit if you want to
  save results with the provided unified interface.

  Example usage:
    >>> experiment = ExampleExperiment()
    >>> experiment.execute()

  here ExampleExperiment is a derived class in which you should implement
  prepare(), run(), get_final_results() and get_params() functions
  (optionally, also get_intermediate_results() which you'll need to call
  yourself inside run(), see corresponding docs). See main.py file for
  an example implementation.

  The call to execute function does the following things:
    1. It reads the optional command line arguments:
       "exp_dir": main directory to store the experiments. Could be outside
       the current folder.

       "exp_name": name of the current experiment, which is the subdirectory
       that is going to be created inside exp_dir with added -run{run number}
       suffix, so if you run the same experiment twice, it's going to save
       both under separate folders. You don't need to provide the run number,
       it is determined automatically: on the first run it's going to create
       exp_dir/exp_name-run1 folder, on the second exp_dir/exp_name-run2, etc.

       "use_old_dir": boolean parameter, indicating whether you want to do the
       usual folder creation or just use exactly exp_dir/exp_name, which could
       be useful for continuing experiments from the saved model.
       The corresponding directory is created.

    2. It adds saving behaviour to get_intermediate_results. For more
       information on that, see corresponding docs.

    3. It calls self.prepare() method: use it to do necessary preparation to
       the training, i.e. arguments parsing, data reading, etc.

    4. It starts logging stdout and changes the current directory to whatever
       directory was created on the first step. Thus, you can save any
       additional information (i.e. tensorflow logs, models) inside the run
       function, assuming you are in the correct experiment folder.

    5. It calls self.get_params() and saves the returned dictionary in
       params.log file. It also adds current git commit information and saves
       git diff in diff.log file so that it's always possible to completely
       replicate the experiments.

    6. It calls self.run() function which should do all the necessary
       computations and prepare the call to get_final_results

    7. It calls self.get_final_results() and saves the results in results.log
       file. That file could already have been created if
       get_intermediate_results() function was used.

    8. It restores get_intermediate_results to the usual behaviour so that
       it could potentially be used later in the code.
  """
  def __init__(self):
    super(BaseExperiment, self).__init__()

  def prepare(self):
    """Experiment preparation function.
    Use this function to read command line parameters, data,
    build tensorflow graph or do whatever is required before
    you can run the actual training.

    If you're using argparse to read command line arguments,
    you have to use parse_known_args instead of parse_args
    since the base experiment also defines some arguments.
    """
    raise NotImplementedError("Implement me...")

  def get_intermediate_results(self):
    """Computation of intermediate results.
    Call this function whenever you want to save some intermediate results.
    For example, if the training takes a lot of time, you might want to
    periodically save validation results, since server might crash or
    you might want to stop the training early and you still want to save
    the last result you've got. If the training finishes till the end,
    this results will be overwritten by whatever the get_final_results
    function returns.

    Note that this function is optional and is not going to be called
    unless you call it yourself inside the run function. It's going
    to be decorated in the execute function with the correct saving
    behavior.

    Args:
      ... whatever you need ...
    Returns:
      dict: {result_name1: result_value1, result_name2: result_value2, ...}
            it's recommended that you provide 'iter': iter_num as one of
            the arguments, since you'll want to know when your experiment
            crashed.
    """
    raise NotImplementedError("Implement me...")

  def get_final_results(self):
    """Computation of the final results.
    This function should return the final results that you want to save
    for your experiment. Note that unlike get_intermediate results, this
    function can't take any additional arguments, so please, store the
    final results in some field and just return them here, if you
    computed everything in the run function.

    Returns:
      dict: {result_name1: result_value1, result_name2: result_value2, ...}
    """
    raise NotImplementedError("Implement me...")

  def run(self):
    """Main training/learning funciton.
    Main training happens here. If you want to save intermediate results,
    you should call get_intermediate_results inside that function as
    frequently, as you want.
    """
    raise NotImplementedError("Implement me...")

  def get_params(self):
    """Function to access the parameters of the experiment.
    This function should return dictionary with all the parameters
    used in the experiment (usually, whatever was parsed from the
    command line or config file).
    The format of the returned dict is {name: value}.

    Returns:
      dict: {pm_name1: pm_value1, pm_name2: pm_value2, ...}
    """
    raise NotImplementedError("Implement me...")

  def _dict_to_string(self, dct):
    """Converts dict to string representation"""
    return "\n".join(["{}: {}".format(name, val) for name, val in dct.items()])

  def _save_params(self, git_hash, git_diff):
    """Helper function that saves parameters of the experiment"""
    params = self.get_params()
    # TODO: make it work with Config?
    with open('params.log', 'w') as fout:
      fout.write("commit hash: {}".format(git_hash))
      fout.write(self._dict_to_string(params))
    with open('git_diff.log', 'w') as fout:
      fout.write(git_diff)

  def _decorate_results_func(self, func):
    """Decorator used to add saving behavior to get_intermediate_results"""
    def wrapped(*args, **kwargs):
      results = func(*args, **kwargs)
      with open('results.log', 'w') as fout:
        fout.write(self._dict_to_string(results))
      return results
    return wrapped

  def execute(self):
    """Main function to call.
    This is the main function for experiment execution (the only one
    that will be called outside this class if you're using the
    provided unified interface.
    """
    parser = argparse.ArgumentParser(description='Experiment params')
    parser.add_argument('--exp_name', default='exp', help='experiment name')
    parser.add_argument('--exp_dir', default='exps', help='experiments folder')
    parser.add_argument(
      '--use_old_dir', default=False, action='store_true',
      help='indicate if you want to reuse existing exp_name/exp_dir',
    )
    args, unknown = parser.parse_known_args()

    old_func = self.get_intermediate_results
    self.get_intermediate_results = self._decorate_results_func(
      self.get_intermediate_results,
    )
    exp_dir = get_output_folder(
      args.exp_name, parent_dir=args.exp_dir,
      create_new=(not args.use_old_dir),
    )
    # calling git here, since might move to the different directory
    # where it is not accessible anymore
    git_hash = get_git_hash()
    git_diff = get_git_diff()
    # prepare function should be called in the original folder since
    # it might read some data assuming the correct relative path
    self.prepare()
    with logging_mode(exp_dir):
      self._save_params(git_hash, git_diff)
      self.run()
      with open('results.log', 'w') as fout:
        results = self.get_final_results()
        fout.write(self._dict_to_string(results))

    self.get_intermediate_results = old_func

