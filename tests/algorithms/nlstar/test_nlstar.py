import unittest
import itertools
import random
from typing import Set, Generator
from inferrer import algorithms
from inferrer.algorithms import Oracle
from inferrer.algorithms.nlstar.observation_table import ObservationTable
from inferrer.algorithms.nlstar.row import Row


class TestLSTAR(unittest.TestCase):

    def test_build_hypothesis_01(self):
        ot = ObservationTable({'a', 'b'}, Oracle(set(), set()))
        row1 = Row('')
        row2 = Row('a')
        row3 = Row('ab')
        row4 = Row('abb')
        row5 = Row('b')
        row6 = Row('aa')

        row7 = Row('aba')
        row8 = Row('abbb')
        row9 = Row('abba')

        ot.suffixes = {'', 'aaa', 'aa', 'a'}

        ot.rows = {row1, row2, row3, row4, row5, row6, row7, row8, row9}

        ot.upper_rows = {row1, row2, row3, row4}
        ot.lower_rows = {row5, row6, row7, row8, row9}

        row1.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 0}
        row2.columns = {'': 0, 'aaa': 1, 'aa': 1, 'a': 0}

        row3.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 1}
        row4.columns = {'': 1, 'aaa': 1, 'aa': 0, 'a': 0}

        row5.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 0}
        row6.columns = {'': 0, 'aaa': 1, 'aa': 1, 'a': 1}
        row7.columns = {'': 1, 'aaa': 1, 'aa': 1, 'a': 0}
        row8.columns = {'': 0, 'aaa': 1, 'aa': 0, 'a': 0}
        row9.columns = {'': 0, 'aaa': 1, 'aa': 1, 'a': 0}

        ot.update_meta_data()

        nlstar = algorithms.NLSTAR({'a', 'b'}, Oracle(set(), set()))
        nlstar._ot = ot

        nfa = nlstar._build_hypothesis()

    def test_lstar_01(self):
        s_plus = {'a' * i for i in range(25)}

        oracle = algorithms.Oracle(s_plus, set())
        nlstar = algorithms.NLSTAR({'a'}, oracle)
        nfa = nlstar.learn()

        self.assertEqual(1, len(nfa._states))
        self.assertEqual(1, len(nfa._accept_states))
        self.assertTrue(nfa.parse_string('a' * 1000)[1])

    def test_nlstar_02(self):
        """
        Try to let NL* learn Kleene plus.
        The alphabet is sigma = {a} and the
        language accepts every string with 1
        or more a's.
        """
        s_plus = {'a', 'aa', 'aaa', 'aaaa', 'aaaaaaaa'}
        s_minus = {''}

        oracle = algorithms.Oracle(s_plus, s_minus)
        nlstar = algorithms.NLSTAR({'a'}, oracle)
        nfa = nlstar.learn()

        self.assertEqual(2, len(nfa._states))
        self.assertEqual(1, len(nfa._accept_states))

    def test_nlstar_03(self):
        s_plus = set()
        s_minus = set()
        for i in self._combinations({'a', 'b'}, 4):
            if i == '':
                s_minus.add(i)
            else:
                s_plus.add(i)

        oracle = algorithms.Oracle(s_plus, s_minus)
        nlstar = algorithms.NLSTAR({'a', 'b'}, oracle)
        nfa = nlstar.learn()

        self.assertEqual(2, len(nfa._states))
        self.assertEqual(1, len(nfa._accept_states))

        for s in s_plus:
            self.assertTrue(nfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(nfa.parse_string(s)[1])

    def test_nlstar_04(self):
        """
        Try to let NL* learn the regular language A.
        A is a language over the alphabet sigma = {a},
        that accepts all strings with an odd number of
        a's.
        """
        s_plus = set()
        s_minus = set()
        for i in range(1, 21, 2):
            s_plus.add('a' * i)
            s_minus.add('a' * (i - 1))

        oracle = algorithms.Oracle(s_plus, s_minus)
        nlstar = algorithms.NLSTAR({'a'}, oracle)
        nfa = nlstar.learn()

        self.assertEqual(2, len(nfa._states))
        self.assertEqual(1, len(nfa._accept_states))

        for s in s_plus:
            self.assertTrue(nfa.parse_string(s)[1])
        for s in s_minus:
            self.assertFalse(nfa.parse_string(s)[1])

    def test_nlstar_05(self):
        """
        try to let NL* learn the regular language A.
        A is a regular language over the alphabet {0, 1} where
        each string contains an odd number of 1s
        """
        random.seed(10012)
        s_plus = set()
        s_minus = {''}
        for i in self._combinations({'0', '1'}, 7):
            if i.count('1') % 2 == 1:
                s_plus.add(i)
            else:
                s_minus.add(i)

        oracle = algorithms.Oracle(s_plus, s_minus)
        nlstar = algorithms.NLSTAR({'0', '1'}, oracle)
        nfa = nlstar.learn()

        for s in s_minus:
            self.assertFalse(nfa.parse_string(s)[1])

    def test_nlstar_06(self):
        """
        try to let NL* learn the regular language A.
        A is a regular language over the alphabet {0, 1} where
        each string contains 101 as a substring.
        """
        s_plus = set()
        s_minus = {''}
        for i in self._combinations({'0', '1'}, 10):
            if len(i) < 3:
                continue
            if '101' in i:
                s_plus.add(i)
            else:
                s_minus.add(i)

        oracle = algorithms.Oracle(s_plus, s_minus)
        nlstar = algorithms.NLSTAR({'0', '1'}, oracle)
        nfa = nlstar.learn()

        for s in s_minus:
            self.assertFalse(nfa.parse_string(s)[1])

    @staticmethod
    def _combinations(s: Set[str], repeat: int) -> Generator:
        for rep in range(repeat + 1):
            for p in itertools.product(s, repeat=rep):
                yield ''.join(p)


if __name__ == '__main__':
    unittest.main()
