# expline
### A simple pipeline to run machine learning experiments

TODO: add description of what is available with this pipeline.

## Installation

Clone the respository and from the base directory run 

    pip install .

## Usage

Look at the docs in the files. To do a test run, execute:

    python example.py -lr=0.1 --epochs=100

and check the created exps/ directory.

To combine the results of different experiments you can run

    combine_results <dir_name>

### Example:
```shell
python example.py -lr=0.1 --epochs=100
python example.py -lr=0.5 --epochs=100
python example.py -lr=0.01 --epochs=100
combine_results.py exps
cat exps.csv
```

Note that ones you install the package, `combine_results` script is available in any directory. 
Alternatively, you can call combine_results function from python
```python
from expline.utils import combine_results
results_csv = combine_results(data_dir)
```

## Dropbox synchronization

Now expline supports synchronization with dropbox. To begin using it you'll need to create a configuration file ~/.explinerc with 2 lines:

    db_token: <db_token>
    db_link: <db_link>

TODO: add explanation to these parameters and how to setup them

Now you can push your experiments folder to central Dropbox server (it's convenient when there are multiple people making experiments at the same time or when you're running experiments on different machines). To do that, execute the following command:
```shell
push_exps <dir_name> --machine_id=<machine_id> --ignore <folder1> <folder2> ... 
```
This will push your folder to Dropbox, prefixing all experiments with machine_id you provide so that there is no accidental overwritting. You can also specify which folders you don't want to sync (that could be your saved models, for example, since they will take too much space).

To pull the centralized experiments folder to your machine and explore it, run
```shell
pull_exps <dir_name> [--overwrite]
```
where dir_name is the name of the directory you want to write it to. If that directory already exists and you want to overwrite it, you'll need to provider --overwrite flag.
