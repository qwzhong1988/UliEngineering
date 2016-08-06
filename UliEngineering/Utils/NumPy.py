#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np

__all__ = ["numpy_resize_insert", "invert_bijection"]

def numpy_resize_insert(arr, val, index, growth_factor=1.5, min_growth=1000, max_growth=1000000):
    """
    Append a value to a 1D numpy array. Resize dynamically if required.
    Returns the new array (which may be the same as the old array).
    No resize is performed if the array is already large enough

    Supports non-continous insertion of values (i.e. index must not grow monotonically).

    After finishing to call numpy_resize_insert, the user must call
    np.resize(arr, actual_size) to trim extra elements from the array.

    The new size is calculate as
    max(min(max(factor_growth, min_growth), max_growth), required_growth)

    Parameters
    ----------
    arr : array_like
        The original array
    val
        The new value to insert
    index : int > 0
        The index to insert value at
    growth_factor : float
        What fraction of the current size the array will be resized to
        in case of a resize
    min_growth : int
        The minimum array growth expressed as number of elements.
        Setting this higher might slightly increase memory overhead,
        but drastically decreases reallocation frequency and therefore significantly increases
        speed.
    max_growth : int
        An upper bound on the extra array size. Setting this too high increases memory overhead,
        but setting it too low will cause too small allocations to occur, resulting in more
        frequent reallocations and therefore more running speed.
    """
    # Array large enough ? If so, we don't have to bother about insertion.
    if index < arr.size:
        arr[index] = val
        return arr
    # OK, need to resize
    required_growth = (index - arr.size) + 1
    factor_growth = int(arr.size * growth_factor)
    # Resize at least min_growth & at most max_growth, but at least required_growth (overrides all other rules)
    growth = max(min(max(factor_growth, min_growth), max_growth), required_growth)
    # Resize (empty space is filled with copies of original array)
    arr = np.resize(arr, arr.size + growth)
    arr[index] = val
    return arr


def invert_bijection(arr):
    """
    Performs an inversion on a bijective array such as arrays
    returned by np.argsort().

    For each value x in the given array at index i,
    the new array will

    Preconditions (not checked):
        - All elements must be >= 0 and < arr.size
        - Array must contain each element < arr.size exactly once
        - Array values must be usable as indices

    Parameters
    ----------
    arr : iterable
        The source array to invert. Must meet the listed preconditions.

    Examples
    --------
    >>> invert_bijection(np.arange(4))
    array([0, 1, 2, 3])
    >>> invert_bijection(np.asarray([1,2,0,3]))
    array([2,0,1,3])
    >>> invert_bijection(np.asarray([1,0,2,3]))
    array([1,0,2,3])
    >>> invert_bijection([1,0,2,3])
    array([1,0,2,3])
    """
    ret = np.zeros_like(arr)
    for new, old in enumerate(arr):
        ret[old] = new
    return ret