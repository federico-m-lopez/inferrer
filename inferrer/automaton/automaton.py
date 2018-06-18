import copy
from inferrer import utils
from inferrer.automaton.state import State
from collections import defaultdict, OrderedDict
from typing import Set, Tuple


class Automaton:

    def __init__(self, alphabet: Set[str], start_state: State=State('')):
        """
        Initiates a deterministic finite automaton

        :param alphabet: The alphabet of the regular language
        :type alphabet: set
        :param start_state: the initial state of the automaton
        :type start_state: State
        """

        self._start_state = start_state

        self._alphabet = alphabet

        self.states = {self._start_state}

        self.accept_states = set()

        self.reject_states = set()

        self._transitions = defaultdict(OrderedDict)

    def add_transition(self, q1: State, q2: State, a: str):
        """
        Adds the transition, delta(q1, a) = q2 to the
        transition table.

        :param q1: from state
        :type q1: automaton.State
        :param q2: to state
        :type q2: automaton.State
        :param a: letter in alphabet
        :type a: str
        """
        if a not in self._alphabet:
            raise ValueError('\'{}\' is not in the alphabet of the automaton!'.format(a))

        self.states.update({q1, q2})
        self._transitions[q1][a] = q2

    def transition_exists(self, q1: State, a: str) -> bool:
        """
        Checks whether the transition
        delta(q1, a) is defined.

        :param q1: from state
        :type q1: automaton.State
        :param a: letter in alphabet
        :type a: str
        :return: True if it exists
        :rtype: bool
        """
        return q1 in self._transitions and \
               a in self._transitions[q1] and \
               self._transitions[q1][a] in self.states

    def transition(self, q1: State, a: str) -> State:
        """
        Performs the transition delta(q1, a) and
        then return the state reached after the
        transition.

        :param q1: from state
        :type q1: automaton.State
        :param a: letter in alphabet
        :type a: str
        :return: to state
        :rtype: automaton.State
        """
        return self._transitions[q1][a]

    def parse_string(self, s: str) -> Tuple[State, bool]:
        """
        Parses each character of the input string through
        the automaton.

        :param s: The string to parse (s element of alphabet*)
        :type s: str
        :return: The state after reading the string s and whether
                 the automaton accepted the input string.
        :rtype: tuple(State, bool)
        """
        q = self._start_state
        for letter in s:
            if not self.transition_exists(q, letter):
                return q, False
            q = self.transition(q, letter)

        return q, q in self.accept_states

    def find_transition_to_q(self, q: State) -> Tuple:
        """
        Finds the State r that satisfies
        delta(q, a) = r where a is a string in the
        alphabet

        :param q: Target state
        :type q: automaton.State
        :return: The state and whether or not the transition exists
        :rtype: tuple(State, str)
        """
        for qf in self._transitions.keys():
            for letter, to_state in self._transitions[qf].items():
                if to_state == q:
                    return qf, letter
        return None, None

    def minimize(self):
        """
        Minimizes the automaton by removing all
        states (and transitions) that cannot be
        reached from the initial state. This is
        done by performing an iterative dept-first
        search over the execution tree given the
        initial state and alphabet.

        :return: minimized dfa
        :rtype: Automaton
        """
        minimized_dfa = Automaton(self._alphabet)

        stack = [State('')]
        visited_states = {State('')}
        while stack:
            state = stack.pop()

            minimized_dfa.states.add(state)

            for a in self._alphabet:
                if state in self._transitions and a in self._transitions[state]:
                    to_state = self.transition(state, a)
                    minimized_dfa.add_transition(state, to_state, a)
                    if to_state not in visited_states:
                        stack.append(to_state)
                        visited_states.add(to_state)

            if state in self.accept_states:
                minimized_dfa.accept_states.add(state)
            elif state in self.reject_states:
                minimized_dfa.reject_states.add(state)

        return minimized_dfa

    def copy(self):
        """
        Performs a deep copy of this instance.

        :return: A copied automaton
        :rtype: Automaton
        """
        cp = Automaton(self._alphabet)

        cp.states = self.states.copy()
        cp.accept_states = self.accept_states.copy()
        cp.reject_states = self.reject_states.copy()
        cp._transitions = copy.deepcopy(self._transitions)

        return cp

    def __str__(self):
        """
        ToString implementation for the class, only used
        for debugging purposes.

        :return: String representation of the dfa
        :rtype: str
        """
        rep = [
            'Initial state:    = {}'.format(self._start_state),
            'Alphabet:         = {}'.format(self._alphabet),
            'States:           = {}'.format(set(map(str, self.states))),
            'Accepting states: = {}'.format(set(map(str, self.accept_states))),
            'Rejecting states: = {}'.format(set(map(str, self.reject_states))),
            '\nTransition function: delta'
        ]

        for state in sorted(self._transitions.keys()):
            rep.append('state = q_{}'.format(state))
            for letter, to_state in self._transitions[state].items():
                rep.append('delta(q_{}, {}) = q_{}'.format(state, letter, to_state))
            rep.append('')

        return '\n'.join(rep)


def build_pta(s_plus: Set[str], s_minus: Set[str]=set()) -> Automaton:
    """
    Function that builds a prefix tree acceptor from the example strings
    S = S+ union S-

    :param s_plus: Set containing positive examples of the target language
    :type s_plus: set
    :param s_minus: Set containing negative examples of the target language
    :type s_minus: set
    :return: An automaton representing a prefix tree acceptor
    :rtype: Automaton
    """
    samples = s_plus.union(s_minus)

    alphabet = utils.determine_alphabet(samples)
    pta = Automaton(alphabet)

    for letter in alphabet:
        pta.add_transition(State(''), State(letter), letter)

    states = {
        State(u) for u in utils.prefix_set(samples, alphabet)
    }

    new_states = set()
    for u in states:
        for a in alphabet:
            ua = State(u.name + a)
            if ua not in states:
                new_states.add(ua)

            pta.add_transition(u, ua, a)

    states.update(new_states)

    for u in states:
        if u.name in s_plus:
            pta.accept_states.add(u)
        if u.name in s_minus:
            pta.reject_states.add(u)

    pta.states = states

    return pta
