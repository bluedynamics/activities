import unittest
import doctest
from interlude import interact

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE

TESTFILES = [
    '../runtime.txt',
]

def test_suite():

    return unittest.TestSuite([
        doctest.DocFileSuite(
            file,
            optionflags=optionflags,
            globs={'interact': interact,},
        ) for file in TESTFILES
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

