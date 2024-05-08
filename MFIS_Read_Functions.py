import numpy as np
import skfuzzy as skf
from MFIS_Classes import *


def readFuzzySetsFile(fleName):
    """
    This function reads a file containing fuzzy set descriptions
    and returns a dictionary with all of them
    """
    fuzzySetsDict = FuzzySetsDict()  # dictionary to be returned
    inputFile = open(fleName, 'r')
    line = inputFile.readline()
    while line != '':
        fuzzySet = FuzzySet()  # just one fuzzy set
        elementsList = line.split(', ')
        print(elementsList)
        setid = elementsList[0]
        var_label = setid.split('=')
        fuzzySet.var = var_label[0]
        fuzzySet.label = var_label[1]

        xmin = int(elementsList[1])
        xmax = int(elementsList[2])
        a = int(elementsList[3])
        b = int(elementsList[4])
        c = int(elementsList[5])
        d = int(elementsList[6])
        x = np.arange(xmin, xmax, 1)
        y = skf.trapmf(x, [a, b, c, d])
        fuzzySet.x = x
        fuzzySet.y = y
        fuzzySetsDict.update({setid: fuzzySet})

        line = inputFile.readline()
    inputFile.close()
    return fuzzySetsDict


def readRulesFile():
    inputFile = open('Files/Rules.txt', 'r')
    rules = RuleList()
    line = inputFile.readline()
    while line != '':
        rule = Rule()
        line = line.rstrip()
        elementsList = line.split(', ')
        rule.ruleName = elementsList[0]
        rule.consequent = elementsList[1]
        lhs = []
        for i in range(2, len(elementsList), 1):
            lhs.append(elementsList[i])
        rule.antecedent = lhs
        rules.append(rule)
        line = inputFile.readline()
    inputFile.close()
    return rules


def readApplicationsFile():
    inputFile = open('Files/Applications.txt', 'r')
    applicationList = []
    line = inputFile.readline()
    while line != '':
        elementsList = line.split(', ')
        app = Application()
        app.appId = elementsList[0]
        app.data = []
        for i in range(1, len(elementsList), 2):
            app.data.append([elementsList[i], int(elementsList[i + 1])])
        applicationList.append(app)
        line = inputFile.readline()
    inputFile.close()
    return applicationList


"""def processApplication(app, inputFuzzySets, outputFuzzySets, rules):
    # step 1: fuzzification
    fuzzify(app, inputFuzzySets)
    # step 2: inference
    appOutY = np.zeros_like(outputFuzzySets[list(outputFuzzySets.keys())[0]].y)  # Initialize output array
    for r in rules:
        # step 2.1: compute strength of the antecedent
        evaluateAntecedent(r, inputFuzzySets)
        # step 2.2: clip the consequent
        evaluateConsequent(r, outputFuzzySets)
        # step 2.3: accumulate the output
        appOutY = composition(r, appOutY)
    # step 3: defuzzification
    first_output_fuzzy_set = list(outputFuzzySets.values())[0]
    appOutX = first_output_fuzzy_set.x
    centroid = skf.centroid(appOutX, appOutY)
    return centroid"""


"""# Hay que hacer las funciones fuzzify, evaluateAntecedent, evaluateConsequent y la de composition
def fuzzify(application, inputFuzzySets):
    for var.value in application.data:
        for set in inputFuzzySets:
            if inputFuzzySets[set].var == var:
                inputFuzzySets[set].memDegree = skf.internp_membership[inputFuzzySets[set].x, inputFuzzySets[set].y, value]




def evaluateAntecedent(rule, inputFuzzySets):
    rule.strength = 1.0
    for ant in rule.antecedent:
        rule.strength = min(rule.strength, inputFuzzySets[ant].memDegree)


def evaluateConsequent(rule, outputFuzzySets):
    rule.consequentX = outputFuzzySets[rule.consequent].x
    rule.consequentY = outputFuzzySets[rule.consequent].y
    rule.consequentY = np.minimum[rule.consequentY, rule.strength]


def composition(rule, appOutY):
    return np.maximun[rule.consequentY, appOutY]"""

