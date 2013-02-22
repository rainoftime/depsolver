import hashlib
import unittest

from depsolver.package \
    import \
        Package
from depsolver.requirement \
    import \
        Requirement
from depsolver.version \
    import \
        Version

V = Version.from_string
R = Requirement.from_string

class TestPackage(unittest.TestCase):
    def test_construction(self):
        r_provides = set()
        r_id = hashlib.md5("numpy-1.3.0").hexdigest()

        package = Package("numpy", V("1.3.0"))
        self.assertEqual(package.provides, r_provides)
        self.assertEqual(package.dependencies, set())
        self.assertEqual(package.id, r_id)

        r_provides = set([R("numpy == 1.3.0")])
        r_id = hashlib.md5("nomkl_numpy-1.3.0").hexdigest()

        package = Package("nomkl_numpy", V("1.3.0"), provides=r_provides)
        self.assertEqual(package.provides, r_provides)
        self.assertEqual(package.id, r_id)

    def test_unique_name(self):
        package = Package("numpy", V("1.3.0"))
        self.assertEqual(package.unique_name, "numpy-1.3.0")

    def test_str(self):
        package = Package("numpy", V("1.3.0"))
        self.assertEqual(str(package), "numpy-1.3.0")

    def test_repr(self):
        package = Package("numpy", V("1.3.0"))
        self.assertEqual(repr(package), "Package('numpy', Version(1, 3, 0))")
