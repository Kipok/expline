from __future__ import print_function
from six.moves import range

import numpy as np
import argparse

from expline.base import BaseExperiment


class ExampleExperiment(BaseExperiment):
  """Example experiment demostrating how to correctly inherit BaseExperiment.

     This class just runs a gradient descent on a simple quadratic function.
  """
  def __init__(self):
    super(ExampleExperiment, self).__init__()

  def prepare(self):
    self.w_init = np.array([-4, 6.0])
    self.b = np.array([2.0, 1.0])
    self.A = np.array([[1, 0.3], [0.3, 0.2]])

    parser = argparse.ArgumentParser(description='GD params')
    parser.add_argument('-lr', '--learning_rate', type=float,
                        help='learning rate', required=True)
    parser.add_argument('-e', '--epochs', required=True,
                        type=int, help='number of epochs')
    # important to use parse_known_args, since some arguments
    # are parsed by the base class
    args, unknown = parser.parse_known_args()

    self.lr = args.learning_rate
    self.T = args.epochs

  def get_params(self):
    return {'lr': self.lr, 'num_epochs': self.T}

  def obj(self, w):
    return 0.5 * w.T.dot(self.A).dot(w) - self.b.dot(w)

  def grad(self, w):
    return self.A.dot(w) - self.b

  def get_intermediate_results(self, w, iter_num):
    obj_val = self.obj(w)
    grad_norm = np.linalg.norm(self.grad(w))
    # note that I'm returning iteration number so that I'll be able
    # to know when I stopped the program or when it crashed
    return {'iter': iter_num, 'objective': obj_val, 'grad_norm': grad_norm}

  def get_final_results(self):
    # I'm assuming, run function was already executed
    obj_val = self.obj(self.w_end)
    grad_norm = np.linalg.norm(self.grad(self.w_end))
    return {'objective': obj_val, 'grad_norm': grad_norm}

  def run(self):
    w_cur = self.w_init.copy()
    for i in range(self.T):
        w_cur -= self.lr * self.grad(w_cur)
        if i % 10 == 0:
          # note, this is going to save the results
          results = self.get_intermediate_results(w_cur, i)
          print("iter #{}".format(i))
          print("\n".join(["  {}: {:.4f}".format(name, val)
                           for name, val in results.items()
                           if name != 'iter']))
    self.w_end = w_cur


if __name__ == '__main__':
  experiment = ExampleExperiment()
  experiment.execute()

