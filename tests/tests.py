#!/usr/bin/python2.7
#encoding utf-8

import unittest
import picking
import numpy as np
import scipy.io as sio


class Check_prctile(unittest.TestCase):

	data = sio.loadmat('signal_fs_50_t0_100.mat')
	x = data['X'][:, 0]
	results = sio.loadmat('test_prctile.mat')
	q = results['q'][0, :]

	def test_results_equal_to_matlab(self):
		for i in xrange(101):
			mq = picking.prctile(self.x, i)
			self.assertTrue(np.allclose(mq, self.q[i]))
		self.assertTrue(np.allclose(picking.prctile(self.x, range(101)), self.q))

	def test_p_not_in_correct_range_should_return_error(self):
		self.assertRaises(ValueError, picking.prctile, self.x, 101)
		self.assertRaises(ValueError, picking.prctile, self.x, [25, -1, 30])

	def test_empty_x_returns_nan(self):
		self.assertTrue(np.isnan(picking.prctile(np.array([]),10)))
		self.assertTrue(np.isnan(picking.prctile(np.array([]),50)))
		self.assertTrue(np.all(np.isnan(picking.prctile(np.array([]),[10, 20]))))


class Check_find_peaks(unittest.TestCase):

	def test_one_peak_returns_correct_result(self):
		x = np.array([1,2,3,4,5,6,5,4,3,2,1])
		self.assertTrue(np.all(picking.find_peaks(x) == np.array([5])))
		self.assertTrue(np.all(picking.find_peaks(x,threshold=0) == np.array([5])))
		self.assertTrue(np.all(picking.find_peaks(x,threshold=10) == np.array([])))
		self.assertTrue(np.all(picking.find_peaks(x,threshold=0,order=5) == np.array([5])))
		self.assertTrue(np.all(picking.find_peaks(x,threshold=0,order=10) == np.array([5])))

	def test_several_peaks_returns_correct_result(self):
		x = np.array([1,6,3,7,5,6,6,4,5,1,1,2,3])
		self.assertTrue(np.all(picking.find_peaks(x) == np.array([3])))
		self.assertTrue(np.all(picking.find_peaks(x,threshold=0) == np.array([1,3,8])))
		self.assertTrue(np.all(picking.find_peaks(x,threshold=10) == np.array([])))
		self.assertTrue(np.all(picking.find_peaks(x,threshold=0, order=3) == np.array([3])))
		self.assertTrue(np.all(picking.find_peaks(x,threshold=0, order=10) == np.array([3])))

	def test_no_peaks_returns_correct_result(self):
		x = np.array([1,1,1,1,1,1,1,1])
		self.assertTrue(np.all(picking.find_peaks(x) == np.array([0])))
		self.assertTrue(np.all(picking.find_peaks(x, threshold=0) == np.array([])))

	def test_empty_signal_returns_empty(self):
		x = np.array([])
		self.assertTrue(np.all(picking.find_peaks(x) == np.array([])))
		self.assertTrue(np.all(picking.find_peaks(x, threshold=0) == np.array([])))

	def test_order_not_positive_returns_error(self):
		x = np.array([1,2,3,4,5,6,5,4,3,2,1])
		self.assertRaises(ValueError, picking.find_peaks, x, 0, 0)
		self.assertRaises(ValueError, picking.find_peaks, x, 0, -1)


class Check_sta_lta(unittest.TestCase):

	data = sio.loadmat('signal_fs_50_t0_100.mat')
	x = data['X'][:, 0]
	results = sio.loadmat('results_sta_5_lta_100.mat')
	cf = results['C'][0, :]
	et = results['T_EVENTO'][0, :]

	def test_signal_returns_correct_results(self):
		et, cf = picking.sta_lta(self.x, 50.0, sta_length=5.0, lta_length=100.0)
		self.assertTrue(np.all(cf == self.cf))
		self.assertTrue(np.all((et / 50.0) == self.et))

	def test_empty_signal_returns_empty(self):
		x = np.array([])
		et, cf = picking.sta_lta(x, 10)
		self.assertTrue(np.all(cf == np.array([])))
		self.assertTrue(np.all(et == np.array([])))

	def test_fs_not_positive_returns_error(self):
		self.assertRaises(ValueError, picking.sta_lta, self.x, 0)
		self.assertRaises(ValueError, picking.sta_lta, self.x, -10)

	def test_sta_length_not_positive_returns_error(self):
		self.assertRaises(ValueError, picking.sta_lta, self.x, 10, sta_length=0)
		self.assertRaises(ValueError, picking.sta_lta, self.x, 10, sta_length=-1)

	def test_lta_length_not_positive_returns_error(self):
		self.assertRaises(ValueError, picking.sta_lta, self.x, 10, lta_length=0)
		self.assertRaises(ValueError, picking.sta_lta, self.x, 10, lta_length=-1)

	def test_sta_greater_than_sta_returns_error(self):
		self.assertRaises(ValueError, picking.sta_lta, self.x, 10, sta_length=15.0, lta_length=10.0)
		self.assertRaises(ValueError, picking.sta_lta, self.x, 10, sta_length=10.0, lta_length=10.0)

	def test_integer_instead_of_float_values_should_return_the_same(self):
		x = self.x.astype(int)
		et, cf = picking.sta_lta(x, 50, sta_length=5, lta_length=100)
		fet, fcf = picking.sta_lta(x.astype(np.float64), 50.0, sta_length=5.0, lta_length=100.0)
		self.assertTrue(np.all(et == fet))
		self.assertTrue(np.all(cf == fcf))


class Check_ampa(unittest.TestCase):

	data = sio.loadmat('signal_fs_50_t0_100.mat')
	x = data['X'][:, 0]
	results = sio.loadmat('results_ampa_default_settings.mat')
	cf = results['ZTOT'][0, :]
	et = results['T_EVENTO'][0, :]

	def test_signal_returns_correct_results(self):
		et, cf = picking.ampa(self.x, 50.0)
		self.assertTrue(np.allclose(cf,self.cf))
		self.assertTrue(np.all((et / 50.0) == self.et))

	def test_fs_not_positive_returns_error(self):
		self.assertRaises(ValueError, picking.ampa, self.x, 0)
		self.assertRaises(ValueError, picking.ampa, self.x, -10)

	def test_noise_thr_not_in_correct_range_should_return_error(self):
		self.assertRaises(ValueError, picking.ampa, self.x, 50, noise_thr=-1)
		self.assertRaises(ValueError, picking.ampa, self.x, 50, noise_thr=110)

	def test_L_empty_or_not_an_iterable_should_return_error(self):
		self.assertRaises(ValueError, picking.ampa, self.x, 50, L=[])

	def test_length_of_x_smaller_than_longest_of_L_should_return_error(self):
		t = 30.0  # 30 seconds
		fs = 50.0  # 50 Hz
		x = np.empty(t * fs)
		self.assertRaises(ValueError, picking.ampa, x, fs, L=[50.0, 20.0])

	def test_L_values_not_positive_should_return_error(self):
		self.assertRaises(ValueError, picking.ampa, self.x, 50, L=[0.0, 10.0])
		self.assertRaises(ValueError, picking.ampa, self.x, 50, L=[10.0, -2.0])

	def test_bandwidth_not_positive_should_return_error(self):
		self.assertRaises(ValueError, picking.ampa, self.x, 50, bandwidth=0.0)
		self.assertRaises(ValueError, picking.ampa, self.x, 50, bandwidth=-1.0)

	def test_bandwidth_too_big_should_return_error(self):
		self.assertRaises(ValueError, picking.ampa, self.x, 50, f_start=2.0, bandwidth=23.0)
		self.assertRaises(ValueError, picking.ampa, self.x, 50, f_start=2.0, bandwidth=50.0)

	def test_overlap_negative_should_return_error(self):
		self.assertRaises(ValueError, picking.ampa, self.x, 50, overlap=-1.0)

	def test_f_start_not_positive_should_return_error(self):
		self.assertRaises(ValueError, picking.ampa, self.x, 50, f_start=0.0)
		self.assertRaises(ValueError, picking.ampa, self.x, 50, f_start=-1.0)

	def test_max_f_end_not_positive_should_return_error(self):
		self.assertRaises(ValueError, picking.ampa, self.x, 50, max_f_end=0.0)
		self.assertRaises(ValueError, picking.ampa, self.x, 50, max_f_end=-1.0)

	def test_f_start_greater_than_max_f_end_should_return_error(self):
		self.assertRaises(ValueError, picking.ampa, self.x, 50, f_start=5.0, max_f_end=5.0)
		self.assertRaises(ValueError, picking.ampa, self.x, 50, f_start=10.0, max_f_end=5.0)

	def test_overlap_greater_than_bandwidth_should_return_error(self):
		self.assertRaises(ValueError, picking.ampa, self.x, 50, bandwidth=5.0, overlap=5.0)
		self.assertRaises(ValueError, picking.ampa, self.x, 50, bandwidth=5.0, overlap=10.0)

	def test_U_not_positive_should_return_error(self):
		self.assertRaises(ValueError, picking.ampa, self.x, 50, f_start=0.0)
		self.assertRaises(ValueError, picking.ampa, self.x, 50, f_start=-1.0)

	def test_integer_instead_of_float_values_should_return_the_same(self):
		x = self.x.astype(int)
		et, cf = picking.ampa(x, 50, L=[30, 20], L_coef=3, bandwidth=3, overlap=1, f_start=2,
			                  max_f_end=12, U=10)
		fet, fcf = picking.ampa(x.astype(np.float64), 50, L=[30, 20], L_coef=3, bandwidth=3,
			                    overlap=1, f_start=2, max_f_end=12, U=10)
		self.assertTrue(np.all(et == fet))
		self.assertTrue(np.all(cf == fcf))


class Check_takanami(unittest.TestCase):

	results = sio.loadmat('test_takanami.mat')
	x = results['x'][:, 0]
	aic = results['AIC_TOTAL'][0, :]
	n0 = results['n0'][0][0]
	n1 = results['n1'][0][0]

	def test_signal_returns_correct_results(self):
		et, aic = picking.takanami(self.x, self.n0, self.n1)
		self.assertTrue(np.allclose(aic, self.aic))

	def test_n0_not_greater_than_k_returns_error(self):
		self.assertRaises(ValueError, picking.takanami, self.x, 6, self.n1, k=6)
		self.assertRaises(ValueError, picking.takanami, self.x, 5, self.n1, k=6)

	def test_length_of_x_minus_n1_not_gt_than_k_returns_error(self):
		self.assertRaises(ValueError, picking.takanami, self.x, self.n0, len(self.x)-6, k=6)
		self.assertRaises(ValueError, picking.takanami, self.x, self.n0, len(self.x)-4, k=6)

	def test_length_of_x_not_greater_than_n1_plus_k_returns_error(self):
		x = np.empty(self.n1 + 6)
		self.assertRaises(ValueError, picking.takanami, x, self.n0, self.n1, k=6)
		self.assertRaises(ValueError, picking.takanami, [], self.n0, self.n1, k=6)

	def test_n0_greater_or_equal_than_n1_returns_error(self):
		self.assertRaises(ValueError, picking.takanami, self.x, self.n0, self.n0)
		self.assertRaises(ValueError, picking.takanami, self.x, self.n0, self.n0-1)

	def test_p_not_positive_returns_error(self):
		self.assertRaises(ValueError, picking.takanami, self.x, self.n0, self.n1, p=0)
		self.assertRaises(ValueError, picking.takanami, self.x, self.n0, self.n1, p=-1)

	def test_k_not_positive_returns_error(self):
		self.assertRaises(ValueError, picking.takanami, self.x, self.n0, self.n1, k=0)
		self.assertRaises(ValueError, picking.takanami, self.x, self.n0, self.n1, k=-1)


if __name__ == "__main__":
	unittest.main()