"""
Test the 4 significant character (right aligned) code 
"""

from unittest import TestCase, main, SkipTest, skip

from Controller import sig4


class TestSig4(TestCase):
    def setUp(self):
        # in case we need some set up
        return

    def tearDown(self):
        # in case we need some tear down
        return

    def testSig4(self):
        """
        Test a variety of points in the 3d space
        to see if they are 'dry' or 'wet'
        """
        valuesOutputs = ((3.14159, "3.14"), 
                         (3.1415,  "3.14"), 
                         (3.14,    "3.14"), 
                         (3.1,     " 3.1"), 
                         (31,      "  31"), 
                         (3,       "   3"), 
                         (31.4159, "31.4"), 
                         (314.15,  "314."),
                         (-3.1415, "-3.1"), 
                         (-3.14,   "-3.1"), 
                         (-3.1,    "-3.1"), 
                         (-31,     " -31"), 
                         (-3,      "  -3"), 
                         (-31.4159,"-31."), 
                         (-314.15, "-314"),
                         ("",      "    "),
                         (None,    "None"),
                         (False,   "Fals"),
                         (True,    "True"),
                         (1 == 2,  "Fals"),
                         (3 == 3,  "True"),
                         ) 
        
        for i in range(len(valuesOutputs)):
            z = valuesOutputs[i][0]
            display = valuesOutputs[i][1]
            with self.subTest(z=z, display=display):
                self.assertEqual(display, sig4(z))
        return

