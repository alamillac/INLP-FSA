#!/usr/bin/env python2.7
# -*- coding: utf8 -*-

import sys
import os
import string
workingDir=os.getcwd()
sys.path.append(workingDir+"/jpbarrette-moman/finenight/python")
from fsa import *

##functions

def clean_dates(list_dates):
    """Recibe una lista de fechas de la forma:
    list_dates = [
        'birth date  [[January 11]], [[1917]]',
        'birth_date  1952|10|20',
        ]

    y retorna una lista con solo la fecha
    cleaned_dates = [
        '[[January 11]], [[1917]]',
        '1952|10|20',
    ]
    """
    return [ date[10:].strip() for date in list_dates if date[:5] == 'birth' and date[6:10] == 'date' ]

class FSADate(object):
    def __init__(self):
        self.__letters = [ char for char in string.letters ]
        self.__digits = [ char for char in string.digits ]
        self.__separators = [ char for char in '],. [|-' ]
        self.__letters2 = [ char for char in '_{}()<>/:!=\'?&~;"*' ]

        self.__alphabet = self.__letters + self.__digits + self.__separators + self.__letters2
        self.__filename_db = 'model_dates.pkl'
        self.__fsa_date_rules = {}
        self.__recognized_db = {}

    def __fsa_recursive(self, alph):
        states0 = { char: 'q0' for char in alph }
        q0 = State("q0", states0, epsilon = ["q1"])
        q1 = State("q1")

        return Nfa([q0, q1], self.__alphabet, q0, [q1]).minimize()

    def build_fsa_separator(self):
        """Construye un FSA que reconoce los separadores de las fechas
        ex:
        ']], [['"""

        return self.__fsa_recursive(self.__separators)

    def build_fsa_all_from_alphabet(self):
        return self.__fsa_recursive(self.__letters + self.__letters2 + self.__separators)

    def save_rules(self, rules):
        try:
            import pickle
            with open(self.__filename_db, 'w') as f:
                pickle.dump(rules, f)
        except:
            pass

    def load_rules(self):
        print "Generando el modelo"

        try:
            import pickle
            with open(self.__filename_db) as f:
                fsa_date_rules = pickle.load(f)
        except:
            fsa_date_rules = self.build_fsa_rules_date()
            self.save_rules(fsa_date_rules)

        self.__fsa_date_rules = fsa_date_rules

        print "Modelo generado"

    def build_fsa_rules_date(self):
        """Construye un FSA que reconoce un texto que contenga una fecha"""

        ANY = self.build_fsa_all_from_alphabet()
        YEAR = self.build_fsa_years()
        MONTH = self.build_fsa_months()
        DAY = self.build_fsa_days()
        SPACE = self.__fsa_recursive([' '])
        SEPARATOR = self.build_fsa_separator()

        # En lugar de hacer un union de todas las reglas y generar un solo FSA decidí crear una lista de varios FSA e iterarlos
        # Esto lo hice debido a la gran cantidad de tiempo que le toma al algoritmo crear la union de todas las reglas
        fsa_rules = {}
        # Regla 1
        # re: ANY SEPARATOR MONTH SEPARATOR DAY SEPARATOR YEAR SEPARATOR ANY
        fsa_rules["ANY SEPARATOR MONTH SEPARATOR DAY SEPARATOR YEAR SEPARATOR ANY"] = \
                    ANY.concatenate(SEPARATOR.concatenate(MONTH.concatenate(SEPARATOR.concatenate(DAY.concatenate(SEPARATOR.concatenate(YEAR.concatenate(SEPARATOR.concatenate(ANY))))))))

        # Regla 2
        # re: ANY SEPARATOR YEAR SEPARATOR MONTH SEPARATOR DAY SEPARATOR ANY
        fsa_rules["ANY SEPARATOR YEAR SEPARATOR MONTH SEPARATOR DAY SEPARATOR ANY"] = \
                    ANY.concatenate(SEPARATOR.concatenate(YEAR.concatenate(SEPARATOR.concatenate(MONTH.concatenate(SEPARATOR.concatenate(DAY.concatenate(SEPARATOR.concatenate(ANY))))))))

        # Regla 3
        # re: ANY SEPARATOR YEAR SEPARATOR ANY
        fsa_rules["ANY SEPARATOR YEAR SEPARATOR ANY"] = \
                    ANY.concatenate(SEPARATOR.concatenate(YEAR.concatenate(SEPARATOR.concatenate(ANY))))

        # Regla 4
        # re: YEAR SEPARATOR MONTH SEPARATOR DAY
        fsa_rules["YEAR SEPARATOR MONTH SEPARATOR DAY"] = \
                    YEAR.concatenate(SEPARATOR.concatenate(MONTH.concatenate(SEPARATOR.concatenate(DAY))))

        # Regla 5
        # re: YEAR
        fsa_rules["YEAR"] = YEAR

        # Regla 6
        # re: MONTH SEPARATOR DAY
        fsa_rules["MONTH SEPARATOR DAY"] = \
                    MONTH.concatenate(SEPARATOR.concatenate(DAY))

        # Regla 7
        # re: ANY SEPARATOR DAY SEPARATOR MONTH SEPARATOR YEAR SEPARATOR ANY
        fsa_rules["ANY SEPARATOR DAY SEPARATOR MONTH SEPARATOR YEAR SEPARATOR ANY"] = \
                    ANY.concatenate(SEPARATOR.concatenate(DAY.concatenate(SEPARATOR.concatenate(MONTH.concatenate(SEPARATOR.concatenate(YEAR.concatenate(SEPARATOR.concatenate(ANY))))))))

        # Regla 8
        # re: MONTH SEPARATOR DAY SEPARATOR YEAR
        fsa_rules["MONTH SEPARATOR DAY SEPARATOR YEAR"] = \
                    MONTH.concatenate(SEPARATOR.concatenate(DAY.concatenate(SEPARATOR.concatenate(YEAR))))

        # Regla 9
        # re: DAY SEPARATOR MONTH SEPARATOR YEAR
        fsa_rules["DAY SEPARATOR MONTH SEPARATOR YEAR"] = \
                    DAY.concatenate(SEPARATOR.concatenate(MONTH.concatenate(SEPARATOR.concatenate(YEAR))))

        # Regla 10
        # re: MONTH SEPARATOR YEAR
        fsa_rules["MONTH SEPARATOR YEAR"] = \
                    MONTH.concatenate(SEPARATOR.concatenate(YEAR))

        # Regla 11
        # re: MONTH SEPARATOR DAY SEPARATOR YEAR SEPARATOR
        fsa_rules["MONTH SEPARATOR DAY SEPARATOR YEAR SEPARATOR"] = \
                    MONTH.concatenate(SEPARATOR.concatenate(DAY.concatenate(SEPARATOR.concatenate(YEAR.concatenate(SEPARATOR)))))

        # Regla 12
        # re: YEAR SEPARATOR MONTH SEPARATOR DAY ANY
        fsa_rules["YEAR SEPARATOR MONTH SEPARATOR DAY ANY"] = \
                    YEAR.concatenate(SEPARATOR.concatenate(MONTH.concatenate(SEPARATOR.concatenate(DAY.concatenate(ANY)))))

        # Regla 13
        # re: ANY SEPARATOR MONTH SEPARATOR DAY SEPARATOR YEAR
        fsa_rules["ANY SEPARATOR MONTH SEPARATOR DAY SEPARATOR YEAR"] = \
                    ANY.concatenate(SEPARATOR.concatenate(MONTH.concatenate(SEPARATOR.concatenate(DAY.concatenate(SEPARATOR.concatenate(YEAR))))))


        return fsa_rules

    def recognize(self, text):
        """
        Indica si el texto contiene alguna fecha o no y en caso de contener una fecha indica las reglas que se ajustan al texto
        """
        if not self.__fsa_date_rules:
            self.load_rules()

        if text in self.__recognized_db:
            # Revisa si este texto ya fue procesado
            return self.__recognized_db[text]

        recognized = False
        recognized_rules = []
        for rule in self.__fsa_date_rules:
            if self.__fsa_date_rules[rule].recognize(text):
                recognized = True
                recognized_rules.append(rule)
        response = (recognized, recognized_rules)

        self.__recognized_db[text] = response

        return response

    def build_fsa_days(self):
        """construye un FSA que reconocera los dias de un mes.
        ex:
        1 o 05 o 13 o 31
        """

        ## del 1 al 9
        fsaNumDaysRule1 = self.__buildFSA('123456789')

        ## del 01 al 09
        fsaPartial1 = self.__buildFSA(['0'])
        fsaNumDaysRule2 = fsaPartial1.concatenate(fsaNumDaysRule1)

        ## del 10 al 29
        fsaPartial2 = self.__buildFSA('12')
        fsaPartial3 = self.__buildFSA('0123456789')
        fsaNumDaysRule3 = fsaPartial2.concatenate(fsaPartial3)

        ## el 30 y 31
        fsaNumDaysRule4 = self.__buildFSA(['30', '31'])

        ## se unen todas las reglas
        fsaDaysRules = [
                fsaNumDaysRule1,
                fsaNumDaysRule2,
                fsaNumDaysRule3,
                fsaNumDaysRule4,
                ]

        return self.__mergeFSA(fsaDaysRules)


    def build_fsa_years(self):
        """construye un FSA que reconocera todas las posibles combinaciones de un año. Esto es:
        1 o 350 o 1998
        """

        states1 = { num: 'q1' for num in '0123456789' }
        states2 = { num: 'q2' for num in '0123456789' }
        states3 = { num: 'q3' for num in '0123456789' }
        states4 = { num: 'q4' for num in '0123456789' }

        q0 = State("q0", states1)
        q1 = State("q1", states2)
        q2 = State("q2", states3)
        q3 = State("q3", states4)
        q4 = State("q4")

        return Nfa([q0, q1, q2, q3, q4], self.__alphabet, q0, [q1, q2, q3, q4]).minimize()

    def build_fsa_months(self):
        """construye un FSA que reconocera todas las posibles combinaciones de un mes. Esto es:
        [Jj]anuary or [Ff]ebruary or ... [Dd]ecember or 01 or 02 or .. 1 or .. 12
        """
        months = ['january',
                'jan',
                'february',
                'feb',
                'march',
                'april',
                'may',
                'june',
                'july',
                'august',
                'september',
                'october',
                'november',
                'december']

        ## Primero se construye un FSA que reconozca todos los meses en texto
        fsaStringMonths = self.__buildFSA(months, True)

        ## Luego el mes en formato numerico puede ser:
        ## del 1 al 9
        fsaNumMonthsRule1 = self.__buildFSA('123456789')

        ## del 01 al 09
        fsaPartial1 = self.__buildFSA(['0'])
        fsaNumMonthsRule2 = fsaPartial1.concatenate(fsaNumMonthsRule1)

        ## del 10 al 12
        fsaPartial2 = self.__buildFSA(['1'])
        fsaPartial3 = self.__buildFSA('012')
        fsaNumMonthsRule3 = fsaPartial2.concatenate(fsaPartial3)

        ## se unen todas las reglas
        fsaMonthsRules = [
                fsaStringMonths,
                fsaNumMonthsRule1,
                fsaNumMonthsRule2,
                fsaNumMonthsRule3
                ]

        return self.__mergeFSA(fsaMonthsRules)

    def __buildFSA(self, list_strings, cap = False):
        """Recibe una lista de textos y crea un FSA con ella.
        Si cap es True el FSA reconoce la primera letra de cada texto en mayuscula o minuscula"""

        if cap:
            string2Fsa = self.__stringCap2Fsa
        else:
            string2Fsa = self.__string2Fsa

        list_fsa = map(lambda s: string2Fsa(s), list_strings)
        return self.__mergeFSA(list_fsa)


    def __mergeFSA(self, list_fsa):
        """Recibe una lista de FSA y los une en uno solo"""

        union_fsa = list_fsa[0]
        for fsa in list_fsa[1:]:
            union_fsa = union_fsa.union(fsa)

        return union_fsa.minimize()

    def __string2Fsa(self, s):
        """Recibe un texto y retorna un FSA del texto"""

        states = map(lambda x:State('q'+str(x),{s[x]:'q'+str(x+1)}),xrange(len(s)))
        states.append(State('q'+str(len(s))))
        initialState = State('q0')
        finalStates = [State('q'+str(len(s)))]
        return Nfa(states, self.__alphabet, initialState, finalStates)

    def __stringCap2Fsa(self, s):
        """Recibe un texto y retorna un FSA del texto que reconoce el primer carater en mayuscula o minuscula.
        Ex:
        september ~ September
        """

        fsa_l = self.__string2Fsa(s[0].lower())
        fsa_u = self.__string2Fsa(s[0].upper())
        fsa_rest = self.__string2Fsa(s[1:])
        fsa_final = fsa_l.union(fsa_u)
        return fsa_final.concatenate(fsa_rest)

#for i in range(len(months)):
    #print unionMonths.recognize(months[i])

def main():
    filename = 'examples_birth_date.txt'
    with open(filename) as dates_file:
        list_dates = clean_dates(dates_file.readlines())

    print "Numero de fechas a evaluar: %d" % len(list_dates)

    fsa_date = FSADate()
    print "Inicio de reconocimientos:"

    rules_stats = {}
    count_recognized = 0
    count_not_recognized = 0
    count_alphabet_errors = 0
    list_not_recognized = []
    i = 0
    for line in list_dates:
        i += 1
        try:
            recognized, rules = fsa_date.recognize(line)
            if recognized:
                for rule in rules:
                    try:
                        rules_stats[rule] += 1
                    except:
                        rules_stats[rule] = 1
                count_recognized += 1
            else:
                count_not_recognized += 1
                list_not_recognized.append(line)
        except AlphabetError as e:
            # Algunos caracteres no están en el alfabeto
            print "%s ... line: %s" % (e, line)
            count_alphabet_errors += 1

        if not i%1000:
            print
            print '===================='
            print '%d lineas analizadas' % i
            print '%d errores con caracteres extraños' % count_alphabet_errors
            print '%d lineas reconocidas' % count_recognized
            print '%d lineas no reconocidas' % count_not_recognized
            print 'Accuracy %.2f' % (float(count_recognized) * 100 / (count_not_recognized + count_recognized))
            print '===================='


    print
    print '===================='
    print 'RESULTADOS:'
    print '--------------------'
    print '%d lineas analizadas' % i
    print '%d errores con caracteres extraños' % count_alphabet_errors
    print '%d lineas reconocidas' % count_recognized
    print '%d lineas no reconocidas' % count_not_recognized
    print 'Accuracy %.2f' % (float(count_recognized) * 100 / (count_not_recognized + count_recognized))
    print
    print 'Estadisticas de reglas:'
    for rule in rules_stats:
        print '%s: %d' % (rule, rules_stats[rule])
    print '===================='

    if count_not_recognized:
        from random import shuffle

        shuffle(list_not_recognized)

        print
        print '===================='
        print 'Lineas no reconocidas (max 10)'
        print '--------------------'
        for line in set(list_not_recognized[:10]):
            print line
        print '===================='


if __name__ == '__main__':
    main()
