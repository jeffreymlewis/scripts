"""
My son's 6th grade class had an assignment to find equations evaluating
to a given TARGET using a set of numbers and basic arithmetic operators
(addition, subtraction, multiplication, division). This is a quick
script to brute force the answer.

Example: Given the set of numbers [1,3,7,16,24] and a target of 11,
write equations using three numbers which evaluate to the target.

7 + 3 + 1 = 11
24 - 16 + 3 = 11

Then do the same for four numbers:

16 - 7 + 3 - 1 = 11

And five numbers

24 + 7 - 16 - 3 - 1 = 11

Etc...
"""

from typing import Callable
from typing import Tuple

import itertools
import math
import operator


class ErrorWrongNumberOfOperators(Exception):
  """
  Raised when the wrong number of operators are passed to the tuple_math() function.
  """


def tuple_math(nums: Tuple[int, ...], operators: Tuple[Callable[[int, int], float]]) -> float:
  """
  Given a tuple of ints and a tuple of mathemtical operators from the
  'operator' module (like operator.add, operator.truedev, etc..)
  return the answer to the given equation.

  For example,
    nums: (1,3,7)
    operators: (operator.sum, operator.sub)
    returns 1 + 3 - 7 = -3
  """
  # check error conditions
  if len(nums)-1 != len(operators):
    raise ErrorWrongNumberOfOperators(f'Expecting exactly {len(nums)-1} operators')

  # check base cases
  if len(nums) == 0:
    return 0
  if len(nums) == 1:
    return nums[0]

  # use the "last" operator on the value of the rest of the equation and the last number.
  return operators[-1](tuple_math(nums[:-1], (operators[:-1])), nums[-1])


def display_answer(nums: Tuple[int, ...],
                   ops: Tuple[Callable[[int, int], float]],
                   target: int,
                   ) -> None:
  """
  Display the answer using proper mathematical syntax.
  """
  operator_mapping = {
    str(operator.add): '+',
    str(operator.sub): '-',
    str(operator.mul): '*',
    str(operator.truediv): '/',
  }

  parenthesis = math.ceil(len(nums) / 2)
  print('(' * parenthesis, end='')
  i = 0
  while i < len(nums):
    print(nums[i], end='')
    if parenthesis and i > 0:
      print(')', end='')
      parenthesis -= 1
    if i < len(ops):
      print(f' {operator_mapping[str(ops[i])]} ', end='')
    i += 1
  print(f' = {target}')


def main():
  """
  Given a list of numbers and a target, find equations that evaluate to
  the target using all available mathematical operations.
  """
  math_ops = [operator.add, operator.sub, operator.mul, operator.truediv]
  nums = [1,3,7,16,24]
  target = 11

  number_of_operands = 5

  # loop through all possible combinations of the input set
  for combination in itertools.combinations(nums, number_of_operands):
    # check all permutations of each combination. Order doesn't matter for
    # addition and multiplication, but it *does* matter for subtraction and
    # division.
    #
    # Depending on the operator, some of these will be redundent, but
    # that's okay.
    for permutation in itertools.permutations(combination):
      # check all possible operations for each permutation
      for ops in itertools.product(math_ops, repeat=len(permutation)-1):
        # print(f'{permutation} of {ops}: {tuple_math(permutation, ops)}')
        if tuple_math(permutation, ops) == target:
          # print(f'{permutation} using {ops}')
          display_answer(permutation, ops, target)


if __name__ == '__main__':
  main()
