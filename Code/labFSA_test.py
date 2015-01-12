#!/usr/bin/env python2.7
# -*- coding: utf8 -*-

from labFSA import  FSADate
import unittest

class FSADateTest(unittest.TestCase):
    """FSADate test"""

    def __init__(self, *args, **kargs):
        super(FSADateTest, self).__init__(*args, **kargs)
        self.fsa_date = FSADate()

    def test_build_fsa_separator(self):
        """Comprueba la funcion que crea un FSA de los separadores de las fechas"""
        test_alph = {
                'a': False,
                'va': False,
                '0a': False,
                'a12': False,
                'fasl3': False,
                '    ': True,
                ']] [[': True,
                ']], [[': True,
                ' ': True,
                ', ': True,
                ',': True,
                ']': True,
                }

        alph_validator = self.fsa_date.build_fsa_separator()
        for test_value in test_alph:
            self.assertEqual(alph_validator.recognize(test_value), test_alph[test_value])


    def test_build_fsa_all(self):
        """Comprueba la funcion que crea un FSA de todo el alfabeto"""

        test_alph = {
                'a': True,
                'va': True,
                '0': False,
                'a12': False,
                'fasl': True,
                'gfsa': True,
                '(asjh': True,
                'ap=pa': True,
                'asd': True,
                '[[23 23 sa]': False,
                'h>  <ds  as': True,
                }

        alph_validator = self.fsa_date.build_fsa_all_from_alphabet()
        for test_value in test_alph:
            self.assertEqual(alph_validator.recognize(test_value), test_alph[test_value])

    def test_build_fsa_dates(self):
        """Comprueba la funcion que crea un FSA de las fechas"""

        test_values = {
                'birth_date [[October 27]], [[1837]] asdas': (True, ["ANY SEPARATOR MONTH SEPARATOR DAY SEPARATOR YEAR SEPARATOR ANY"]),
                '[[October 27]], [[1837]]': (True, ["ANY SEPARATOR MONTH SEPARATOR DAY SEPARATOR YEAR SEPARATOR ANY"]),
                'birth_date [[ctober]], [[]]': (False, []),
                'birth_date 1975|10|27 asd': (True, ["ANY SEPARATOR YEAR SEPARATOR MONTH SEPARATOR DAY SEPARATOR ANY"]),
                '1975|h': (False, []),
                'f-1975': (False, []),
                'f-1975-': (False, []),
                'f[1975]': (False, []),
                'f[1975hh': (False, []),
                'ff1975hh': (False, []),
                'f 1975 h': (True, ["ANY SEPARATOR YEAR SEPARATOR ANY"]),
                'f[1975]h': (True, ["ANY SEPARATOR YEAR SEPARATOR ANY"]),
                'f-197|h': (True, ["ANY SEPARATOR YEAR SEPARATOR ANY"]),
                'f 97|h': (True, ["ANY SEPARATOR YEAR SEPARATOR ANY"]),
                'f-1975 h': (True, ["ANY SEPARATOR YEAR SEPARATOR ANY"]),
                'f 195 h': (True, ["ANY SEPARATOR YEAR SEPARATOR ANY"]),
                'a[[1954]]fasd': (True, ["ANY SEPARATOR YEAR SEPARATOR ANY"]),
                '[[1954]]': (True, ["ANY SEPARATOR YEAR SEPARATOR ANY"]),
                '1954|12|30': (True, ["YEAR SEPARATOR MONTH SEPARATOR DAY"]),
                '5|July|30': (True, ["DAY SEPARATOR MONTH SEPARATOR YEAR", "YEAR SEPARATOR MONTH SEPARATOR DAY"]),
                '4  July  30': (True, ["DAY SEPARATOR MONTH SEPARATOR YEAR", "YEAR SEPARATOR MONTH SEPARATOR DAY"]),
                '154|Jly|30': (False, []),
                '4 30': (True, ["MONTH SEPARATOR DAY", "MONTH SEPARATOR YEAR"]),
                '430': (True, ["YEAR"]),
                '15 30': (False, []),
                '4 32': (True, ["MONTH SEPARATOR YEAR"]),
                'April 30': (True, ["MONTH SEPARATOR DAY", "MONTH SEPARATOR YEAR"]),
                '[[June 4]], [[1867]], [[Askainen]]': (True, ["ANY SEPARATOR MONTH SEPARATOR DAY SEPARATOR YEAR SEPARATOR ANY"]),
                '[[7 March]] [[1975]]': (True, ["ANY SEPARATOR DAY SEPARATOR MONTH SEPARATOR YEAR SEPARATOR ANY"]),
                '[[7 03]] [[1975]]': (True, ["ANY SEPARATOR DAY SEPARATOR MONTH SEPARATOR YEAR SEPARATOR ANY", "ANY SEPARATOR MONTH SEPARATOR DAY SEPARATOR YEAR SEPARATOR ANY"]),
                '[[7 3]] [[1975]]': (True, ["ANY SEPARATOR DAY SEPARATOR MONTH SEPARATOR YEAR SEPARATOR ANY", "ANY SEPARATOR MONTH SEPARATOR DAY SEPARATOR YEAR SEPARATOR ANY"]),
                '[[37 31]] [[1975]]': (False, []),
                'May 31, 1945': (True, ["MONTH SEPARATOR DAY SEPARATOR YEAR"]),
                '20 September 1958': (True, ["DAY SEPARATOR MONTH SEPARATOR YEAR"]),
                'November, 1954': (True, ["MONTH SEPARATOR YEAR"]),
                'January 17, [[1945]]': (True, ["MONTH SEPARATOR DAY SEPARATOR YEAR SEPARATOR"]),
                '[[12 Feb]] [[1970]]': (True, ["ANY SEPARATOR DAY SEPARATOR MONTH SEPARATOR YEAR SEPARATOR ANY"]),
                '1957|5|28,': (True, ["YEAR SEPARATOR MONTH SEPARATOR DAY ANY"]),
                '[[April 20]], 1586': (True, ["ANY SEPARATOR MONTH SEPARATOR DAY SEPARATOR YEAR"]),

                }

        validator = self.fsa_date
        for test_value in test_values:
            #print test_value
            self.assertEqual(validator.recognize(test_value), test_values[test_value])

    def test_build_fsa_days(self):
        """Comprueba la funcion que crea un FSA de los dias"""

        test_days = {
                '00': False,
                '01': True,
                '07': True,
                '09': True,
                '9': True,
                '1': True,
                '6': True,
                '0': False,
                '10': True,
                '12': True,
                '13': True,
                '21': True,
                '31': True,
                '32': False,
                '0921': False,
                '91': False,
                '191': False,
                '1913': False,
                '9913': False,
                'jt913': False,
                't913': False,
                '11913': False,
                '11913': False,
                't': False,
                '2342342401913': False,
                }

        days_validator = self.fsa_date.build_fsa_days()
        for test_value in test_days:
            self.assertEqual(days_validator.recognize(test_value), test_days[test_value])

    def test_build_fsa_years(self):
        """Comprueba la funcion que crea un FSA de los años"""

        test_years = {
                '00': True,
                '01': True,
                '07': True,
                '09': True,
                '9': True,
                '1': True,
                '6': True,
                '0': True,
                '10': True,
                '12': True,
                '13': True,
                '21': True,
                '0921': True,
                '91': True,
                '191': True,
                '1913': True,
                '9913': True,
                'jt913': False,
                't913': False,
                '11913': False,
                '11913': False,
                't': False,
                '2342342401913': False,
                }

        year_validator = self.fsa_date.build_fsa_years()
        for test_value in test_years:
            self.assertEqual(year_validator.recognize(test_value), test_years[test_value])

    def test_build_fsa_months(self):
        """Comprueba la funcion que crea un FSA de los meses"""

        test_months = {
                'January': True,
                'january': True,
                'Januar': False,
                'anuary': False,
                'December': True,
                'december': True,
                'decemberr': False,
                'ddecember': False,
                'ecember': False,
                'Decembe': False,
                '00': False,
                '01': True,
                '07': True,
                '09': True,
                '9': True,
                '1': True,
                '6': True,
                '0': False,
                '10': True,
                '12': True,
                '13': False,
                '21': False,
                '921': False,
                '91': False,
                '191': False
                }

        month_validator = self.fsa_date.build_fsa_months()
        for test_month in test_months:
            self.assertEqual(month_validator.recognize(test_month), test_months[test_month])

if __name__ == '__main__':
    unittest.main()
