import unittest

from jb_vpc_cidrcalc.handlers import CIDR
from jb_vpc_cidrcalc.handlers import Lister

cidr_maps = {
    16: 28,
    32: 27,
    64: 26,
    128: 25,
    256: 24,
    512: 23,
    1000: 22,
    2000: 21,
    4000: 20,
    8000: 19,
    16000: 18,
    32000: 17,
    64000: 16
}


class CalculatorTests(unittest.TestCase):

    def test_instantiation(self):
        cidr = CIDR('10.0.0.0', 22)
        self.assertEqual(cidr.number_of_hosts, 22)
        self.assertEqual(cidr.starting_address, '10.0.0.0')
        self.assertDictEqual(cidr_maps, cidr.map)

    def test_next_cidr(self):
        cidr = CIDR('10.0.0.0', 250)
        next_cidr = cidr.get_cidr()
        self.assertEqual(next_cidr, '10.0.0.0/24')

    def test_out_of_range(self):
        with self.assertRaises(ValueError):
            cidr = CIDR('10.0.0.0', 64001)
            cidr.get_cidr()

    def test_split_by_prefix(self):
        cidr = CIDR(None, None)
        expected_list = ['10.0.0.0/26', '10.0.0.64/26',
                         '10.0.0.128/26', '10.0.0.192/26']
        self.assertEqual(cidr.split_by_prefix(
            '10.0.0.0/24', 26), expected_list)


class GeneratorTests(unittest.TestCase):

    def test_split_by_hosts(self):
        cidrs = Lister().split_by_host_numbers(
            '10.0.0.0', [64, 128, 64, 250, 500])
        expected_list = ['10.0.0.0/26', '10.0.0.128/25',
                         '10.0.1.0/26', '10.0.2.0/24', '10.0.4.0/23']
        self.assertEqual(cidrs, expected_list)

    def test_split_by_prefix(self):
        cidrs = Lister().split_by_prefix('10.0.0.0/24', 26)
        expected_list = ['10.0.0.0/26', '10.0.0.64/26',
                         '10.0.0.128/26', '10.0.0.192/26']
        self.assertEqual(cidrs, expected_list)

    def test_out_of_range(self):
        with self.assertRaises(ValueError):
            cidrs = Lister().split_by_host_numbers(
                '10.0.0.0', [64, 128, 64, 250, 500000])


if __name__ == "__main__":
    unittest.main()
