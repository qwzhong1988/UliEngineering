#!/usr/bin/env python3
import numpy as np
from nose.tools import assert_equal, assert_true, raises, assert_in, assert_not_in, assert_is_instance
from numpy.testing import assert_array_equal, assert_array_less, assert_allclose
from UliEngineering.SignalProcessing.Filter import *
from UliEngineering.SignalProcessing.Filter import _normalize_frequencies
from nose_parameterized import parameterized

class TestFilter(object):

    def __init__(self):
        self.d = np.random.random(1000)
        # Some rather random test filter
        self.filt = SignalFilter(100.0, [1.0, 2.0], btype="bandpass")
        self.filt.iir(order=2, rp=1)

    @parameterized([
        ("lowpass", 1.0),
        ("highpass", 1.0),
        ("bandpass", [1.0, 2.0]),
        ("bandstop", [1.0, 2.0]),
    ])
    def testBasicFilter(self, btype, frequencies):
        filt = SignalFilter(100.0, frequencies, btype=btype)
        filt.iir(order=3)
        d2 = filt(self.d)
        assert_equal(self.d.shape, d2.shape)

    @parameterized([
        ("butter",),
        ("cheby1",),
        ("cheby2",),
        ("ellip",),
        ("bessel",),
    ])
    def testFilterTypes(self, ftype):
        filt = SignalFilter(100.0, [1.0, 2.0], btype="bandpass")
        filt.iir(order=3, ftype=ftype)
        d2 = filt(self.d)
        assert_equal(self.d.shape, d2.shape)

    @raises(ValueError)
    def testInvalidPassType(self):
        filt = SignalFilter(100.0, [1.0, 2.0], btype="foobar")

    def test_normalize_frequencies(self):
        assert_allclose(1200., _normalize_frequencies(1200.))
        assert_allclose(1200., _normalize_frequencies("1.2 kHz"))
        assert_allclose(1.0, _normalize_frequencies([1.0]))
        assert_allclose(1.0, _normalize_frequencies(["1 Hz"]))
        assert_allclose([1.0, 2.0], _normalize_frequencies([1.0, 2.0]))
        assert_allclose([1.0, 2.0], _normalize_frequencies(["1 Hz", "2 Hz"]))

    @raises(ValueError)
    def test_normalize_frequencies_invalid(self):
        _normalize_frequencies(None)

    def testFrequencyResponse(self):
        filt = SignalFilter(100.0, [1.0, 2.0], btype="bandpass")
        filt.iir(order=3)
        filt.frequency_response()

    @parameterized([
        ("lowpass", 1.0),
        ("highpass", 1.0),
        ("bandpass", [1.0, 2.0]),
        ("bandstop", [1.0, 2.0]),
        ("lowpass", [1.0]),
        ("highpass", [1.0]),
        ("lowpass", "1.0"),
        ("highpass", "1.0"),
        ("lowpass", ["1.0"]),
        ("highpass", ["1.0"]),
        ("bandpass", ["1.0", "2.0"]),
        ("bandstop", ["1.0", "2.0"]),
        ("lowpass", "1.0 kHz"),
        ("lowpass", "47.532 µHz"),
    ])
    def testCorrectFrequencyParam(self, btype, freqs):
        SignalFilter(100.0, freqs, btype)

    @parameterized([
        ("lowpass", None),
        ("highpass", None),
        ("bandpass", None),
        ("bandstop", None),
        ("lowpass", [1.0, 2.0]),
        ("highpass", [1.0, 2.0]),
        ("bandpass", 1.0),
        ("bandstop", 1.0),
        ("lowpass", [1.0, 2.0, 3.0]),
        ("highpass", [1.0, 2.0, 3.0]),
        ("bandpass", [1.0, 2.0, 3.0]),
        ("bandstop", [1.0, 2.0, 3.0]),
        ("bandstop", []),
        ("lowpass", "foobar"),
        ("highpass", "foobar"),
        ("bandpass", "foobar"),
        ("bandstop", "foobar"),
    ])
    @raises(ValueError)
    def testWrongFrequencyParam(self, btype, freqs):
        SignalFilter(100.0, freqs, btype)

    @raises(NotComputedException)
    def testUninitializedFilter1(self):
        filt = SignalFilter(100.0, 1.0)
        filt.is_stable()

    @raises(NotComputedException)
    def testUninitializedFilter2(self):
        filt = SignalFilter(100.0, 1.0)
        filt(self.d)

    @raises(FilterUnstableError)
    def testUnstableFilter(self):
        filt = SignalFilter(100.0, [1.0, 2.0], btype="bandpass")
        filt.iir(order=100, rp=1e-12)

    def testAsSamplerate(self):
        # TODO improve test
        self.filt.as_samplerate(100.)
        self.filt.as_samplerate(200.)
        self.filt.as_samplerate(50.)

    @raises(NotComputedException)
    def testAsSamplerateNotComputed(self):
        # TODO improve test
        filt = SignalFilter(100.0, [1.0, 2.0], btype="bandpass")
        filt.as_samplerate(100.)

    def testChain(self):
        assert_is_instance(self.filt.chain(5), ChainedFilter)
        assert_is_instance(self.filt.chain(1), SignalFilter)
        # chain_with
        assert_is_instance(self.filt.chain_with(self_repeat=1), SignalFilter)
        assert_is_instance(self.filt.chain_with(self_repeat=2), ChainedFilter)
        assert_is_instance(self.filt.chain_with(other=self.filt,
                               self_repeat=2, other_repeat=2), ChainedFilter)


    @raises(ValueError)
    def testChain0(self):
        "Test chain with repeat=0"
        self.filt.chain(0)




class TestChainedFilter(TestFilter):

    @parameterized([
        ("lowpass", 1.0),
        ("highpass", 1.0),
        ("bandpass", [1.0, 2.0]),
        ("bandstop", [1.0, 2.0]),
    ])
    def testBasic(self, btype, frequencies):
        filt = SignalFilter(100.0, 1.0, btype="lowpass").iir(order=3)
        cfilt = ChainedFilter([filt, filt])
        d2 = cfilt(self.d)
        assert_equal(self.d.shape, d2.shape)
        # Check repeat
        cfilt = ChainedFilter(filt, repeat=4)
        d2 = cfilt(self.d)
        assert_equal(self.d.shape, d2.shape)
        assert_true(cfilt.is_stable())
        # Check +=
        len1 = len(cfilt)
        cfilt += filt
        d2 = cfilt(self.d)
        assert_equal(len(cfilt), len1 + 1)
        assert_equal(self.d.shape, d2.shape)

    def testFrequencyResponse(self):
        testFilter = SignalFilter(400.0, 100.0, btype="lowpass").iir(1, ftype="butter")
        fx0, fy0 = testFilter.frequency_response()
        fx1, fy1 = ChainedFilter(testFilter, repeat=1).frequency_response()
        fx2, fy2 = ChainedFilter(testFilter, repeat=2).frequency_response()
        # Shapes should all match
        assert_equal(fx0.shape, fy0.shape)
        assert_equal(fx1.shape, fy1.shape)
        assert_equal(fx2.shape, fy2.shape)
        assert_equal(fx0.shape, fx1.shape)
        assert_equal(fx1.shape, fx2.shape)
        assert_equal(fy0.shape, fy1.shape)
        assert_equal(fy1.shape, fy2.shape)
        # X should be all equal
        assert_allclose(fx0, fx1)
        assert_allclose(fx1, fx2)
        # Y with repeat=1 should be equal
        assert_allclose(fy0, fy1)
        # fy2 filters more -> should be less
        assert_array_less(fy2, fy1)
        # Check samplerate
        assert_equal(ChainedFilter(testFilter, repeat=1).samplerate, 400.)
        assert_equal(ChainedFilter(testFilter, repeat=2).samplerate, 400.)
        assert_equal(ChainedFilter(testFilter, repeat=3).samplerate, 400.)
        # Check as_samplerate (basic check)
        cf = ChainedFilter(testFilter, repeat=1)
        cf400 = cf.as_samplerate(400.)  # Same samplerate => shortcut
        cf500 = cf.as_samplerate(500.)
        assert_true(cf400 == cf)
        assert_true(cf500 != cf)

    @raises(FilterInvalidError)
    def testDifferingSamplerateFilters(self):
        testFilter1 = SignalFilter(400.0, 100.0, btype="lowpass").iir(1, ftype="butter")
        testFilter2 = SignalFilter(400.0, 10.0, btype="lowpass").iir(1, ftype="butter")
        testFilter3 = SignalFilter(100.0, 20.0, btype="lowpass").iir(1, ftype="butter")
        ChainedFilter([testFilter1, testFilter2, testFilter3])

    @raises(ValueError)
    def testEmptyList(self):
        ChainedFilter([])


class TestSumFilter(TestFilter):
    @parameterized([
        ("lowpass", 1.0),
        ("highpass", 1.0),
        ("bandpass", [1.0, 2.0]),
        ("bandstop", [1.0, 2.0]),
    ])
    def testBasic(self, btype, frequencies):
        filt = SignalFilter(100.0, 1.0, btype="lowpass").iir(order=3)
        sfilt = SumFilter([filt, filt])
        d2 = sfilt(self.d)
        assert_equal(self.d.shape, d2.shape)
        assert_true(sfilt.is_stable())
        # Check +=
        len1 = len(sfilt)
        sfilt += filt
        d2 = sfilt(self.d)
        assert_equal(len(sfilt), len1 + 1)
        assert_equal(self.d.shape, d2.shape)

    def testSingleFilterConstructor(self):
        filt = SignalFilter(100.0, 1.0, btype="lowpass").iir(order=3)
        SumFilter(filt)

class TestFilterBank(object):
    def testBasic(self):
        filt1 = SignalFilter(100.0, 1.0, btype="lowpass").iir(order=1)
        filt2 = SignalFilter(100.0, 2.0, btype="lowpass").iir(order=1)
        bank = FilterBank(100.)
        bank["A"] = filt1
        bank["B"] = filt2
        # Check 100 Hz bank
        assert_in("A", bank)
        assert_in("B", bank)
        assert_not_in(filt1, bank)
        assert_not_in(bank, bank)
        # Check fast path resampling to same samplerate
        assert_true(bank.as_samplerate(100.) == bank)
        # Check resampled bank
        bank200 = bank.as_samplerate(200.)
        assert_true(bank200 != bank)
        assert_in("A", bank200)
        assert_in("B", bank200)
        assert_equal(bank200["A"].samplerate, 200.)
        assert_equal(bank200["B"].samplerate, 200.)
