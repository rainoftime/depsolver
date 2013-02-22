import re

from collections import OrderedDict

_IS_VALID_LITERAL = re.compile("[a-zA-Z_0-9][-+.\w\d]*")

class Literal(object):
    """Creates a simple Literal to be used within clauses.

    Parameters
    ----------
    name: str
        Name of the literal (must consists of alphanumerical characters only)
    """
    def __init__(self, name):
        if not _IS_VALID_LITERAL.match(name):
            raise ValueError("Invalid literal name: %s" % name)
        self._name = name

    @property
    def name(self):
        return self._name

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.name == other._name

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        return "L('%s')" % self.name

    def __or__(self, other):
        return Clause([self, other])

    def __invert__(self):
        return Not(self.name)

    def evaluate(self, values):
        if not self.name in values:
            raise ValueError("literal %s is undefined" % self.name)
        else:
            return values[self.name]

class Not(Literal):
    def __repr__(self):
        return "L('~%s')" % self.name

    def evaluate(self, values):
        return not super(Not, self).evaluate(values)

class Clause(object):
    @classmethod
    def from_string(cls, clause_string):
        literals = []
        for literal_string in clause_string.split("|"):
            literal_string = literal_string.strip()
            if literal_string.startswith("~"):
                if len(literal_string) < 2:
                    raise ValueError("Invalid literal string: %r" % literal_string)
                else:
                    literals.append(Not(literal_string[1:]))
            else:
                literals.append(Literal(literal_string))
        return cls(literals)

    def __init__(self, literals):
        self._literals = frozenset(literals)
        self._literals_set = frozenset(l.name for l in literals)

        self._name_to_literal = dict((literal.name, literal) for literal in literals)

    @property
    def is_assertion(self):
        return len(self._literals) == 1

    @property
    def literals(self):
        return self._literals

    @property
    def literal_names(self):
        return self._literals_set

    def get_literal(self):
        if self.is_assertion:
            return iter(self._literals).next()
        else:
            raise ValueError("Cannot get literal from non-assertion clause !")

    def evaluate(self, values):
        ret = False
        for literal in self.literals:
            if not literal.name in values:
                raise ValueError("literal %s value is undefined" % (literal.name,))
            else:
                ret |= literal.evaluate(values)
        return ret

    def satisfies_or_none(self, values):
        """Return True if the clause is satisfied, False if not, None if it
        cannot be evaluated."""
        unset_literals = []
        for literal in self.literals:
            if literal.name in values:
                if literal.evaluate(values):
                    return True
            else:
                unset_literals.append(literal)
        if len(unset_literals) > 0:
            return None
        else:
            return False

    def __or__(self, other):
        if isinstance(other, Clause):
            literals = set(self.literals)
            literals.update(other.literals)
            return Clause(literals)
        elif isinstance(other, Literal):
            literals = set([other])
            literals.update(self.literals)
            return Clause(literals)
        else:
            raise TypeError("unsupported type %s" % type(other))

    def __repr__(self):
        def _simple_literal(l):
            return "~%s" % l.name if isinstance(l, Not) else l.name
        return "C({})".format(" | ".join(_simple_literal(l) for l in self.literals))

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.literals == other.literals

    def __hash__(self):
        return hash(self.literals)

def _find_unset_variable(clauses, variables):
    for clause in clauses:
        for l in clause.literal_names:
            if not l in variables:
                return l
    return None

def _try_evaluate(clauses, variables):
    unset = _find_unset_variable(clauses, variables)
    if unset is not None:
        variables[unset] = True
        is_satisfiable, new_variables = _try_evaluate(clauses, variables)
        if is_satisfiable:
            return is_satisfiable, new_variables
        else:
            variables[unset] = False
            is_satisfiable, new_variables = _try_evaluate(clauses, variables)
            if is_satisfiable:
                return is_satisfiable, new_variables
            else:
                variables.popitem()
                return False, variables
    else:
        for clause in clauses:
            if not clause.evaluate(variables):
                return False, variables
        return True, variables

def is_satisfiable(clauses, variables=None):
    """A naive back-tracking implementation of SAT solver.
    
    Parameters
    ----------
    clauses: set
        Set of clauses instance. The set is considered as a conjunction of
        clauses
    variables: mapping
        OrderedDict containing pre-defined variables -> boolean.

    Returns
    -------
    satisfiability: bool
        True if the given instance is satisfiable
    variables: mapping
        If satisfiable, gives one found solution. The solution is a simple
        mapping variable name -> boolean.
    """
    if variables is None:
        variables = OrderedDict()
    result, result_variables = _try_evaluate(clauses, variables)
    return result, dict(result_variables)