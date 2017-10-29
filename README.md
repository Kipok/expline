# expline
### A simple pipeline to run machine learning experiments

## Installation

Clone the respository and from the base direcroty run 

    $ pip install .

## Usage

Look at the docs in the files. To do a test run, execute:

    $ python example.py -lr=0.1 --epochs=100

and check the created exps/ directory.

To combine the results of different experiments you can run

    $ combine_results <dir_name>

### Example:

    $ python example.py -lr=0.1 --epochs=100
    $ python example.py -lr=0.5 --epochs=100
    $ python example.py -lr=0.01 --epochs=100
    $ combine_results.py exps
    $ cat exps.csv

Note that after you install the package `combine_results` script is available in any directory. 
Alternatively, you can call combine_results function from python
```python
    from expline.utils import combine_results
    results_csv = combine_results(data_dir)
```
