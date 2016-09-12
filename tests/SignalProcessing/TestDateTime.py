#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from numpy.testing import assert_approx_equal, assert_allclose, assert_array_equal
from nose.tools import assert_equal, assert_true, raises, assert_less, assert_is_none, assert_raises
from UliEngineering.SignalProcessing.DateTime import *
from nose_parameterized import parameterized
import concurrent.futures
import numpy as np
import datetime

class TestSpliceDate(object):
    def test_simple(self):
        d1 = datetime.datetime(2016, 1, 1, 12, 32, 15, microsecond=123456)
        d2 = datetime.datetime(1905, 1, 1, 14, 11, 25, microsecond=52)
        dres = datetime.datetime(2016, 1, 1, 14, 11, 25, microsecond=52)
        assert_equal(dres, splice_date(d1, d2))