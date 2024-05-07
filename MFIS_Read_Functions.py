#!/usr/bin/env python3
import numpy as np
import skfuzzy as skf
import matplotlib.pyplot as plt
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


def processApplication(app, inputFuzzySets, outputFuzzySets, rules):
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
    return centroid


# Hay que hacer las funciones fuzzify, evaluateAntecedent, evaluateConsequent y la de composition
def fuzzify(application, inputFuzzySets):
    """
    Fuzzify the application data based on the input fuzzy sets.

    Parameters:
    - application: Application object containing data to be fuzzified
    - inputFuzzySets: Dictionary of input fuzzy sets

    Modifies the 'application' object by adding fuzzified values.
    """
    for data_pair in application.data:
        var_name, value = data_pair
        if var_name in inputFuzzySets:
            fuzzy_set = inputFuzzySets[var_name]
            # Calculate membership degree using numpy interp
            membership_degree = np.interp(value, fuzzy_set[:, 0], fuzzy_set[:, 1])
            # Store membership degree in the application object
            data_pair.append(membership_degree)
        else:
            raise ValueError(f"Undefined fuzzy set for variable '{var_name}'")


def custom_membership_function(value, fuzzy_set):
    """
    Custom membership function for calculating membership degree.
    For simplicity, let's use a trapezoidal membership function.

    Parameters:
    - value: Input value to be evaluated
    - fuzzy_set: FuzzySet object containing fuzzy set parameters

    Returns:
    - membership_degree: Degree of membership of 'value' in 'fuzzy_set'
    """
    xmin, xmax = fuzzy_set.x[0], fuzzy_set.x[-1]
    a, b, c, d = fuzzy_set.a, fuzzy_set.b, fuzzy_set.c, fuzzy_set.d

    if value <= a or value >= d:
        return 0.0
    elif a < value < b:
        return (value - a) / (b - a)
    elif b <= value <= c:
        return 1.0
    elif c < value <= d:
        return (d - value) / (d - c)
    else:
        return 0.0


def evaluateAntecedent(rule, inputFuzzySets):
    """
    Evaluate the antecedent of the rule by computing the strength of the antecedent.

    Parameters:
    - rule: Rule object containing rule information
    - inputFuzzySets: Dictionary of input fuzzy sets

    Modifies the 'rule' object by setting its 'strength' attribute.
    """
    strength = 1.0
    for condition in rule.antecedent:
        var_name, value = condition.split('=')
        value = float(value)

        if var_name in inputFuzzySets:
            fuzzy_set = inputFuzzySets[var_name]
            # Calculate membership degree using a custom membership function
            membership_degree = custom_membership_function(value, fuzzy_set)
            # Take the minimum of current strength and membership degree
            strength = min(strength, membership_degree)
        else:
            raise ValueError(f"Undefined fuzzy set for variable '{var_name}'")

    rule.strength = strength


def evaluateConsequent(rule, outputFuzzySets):
    """
    Evaluate the consequent of the rule by clipping the output fuzzy sets.

    Parameters:
    - rule: Rule object containing rule information
    - outputFuzzySets: Dictionary of output fuzzy sets

    Modifies the 'rule' object by setting its 'clipped_consequent' attribute.
    """
    if rule.consequent in outputFuzzySets:
        fuzzy_set = outputFuzzySets[rule.consequent]
        # Clip the output fuzzy set based on rule strength
        clipped_consequent = clip_fuzzy_set(fuzzy_set, rule.strength)
        rule.clipped_consequent = clipped_consequent
    else:
        raise ValueError(f"Undefined fuzzy set for consequent '{rule.consequent}'")


def clip_fuzzy_set(fuzzy_set, strength):
    """
    Clip a fuzzy set based on a given strength.

    Parameters:
    - fuzzy_set: FuzzySet object containing fuzzy set parameters
    - strength: Strength of the rule

    Returns:
    - clipped_fuzzy_set: Clipped fuzzy set array
    """
    clipped_fuzzy_set = np.minimum(fuzzy_set.y, strength)
    return clipped_fuzzy_set


def composition(rule, appOutY):
    """
    Accumulate the clipped consequents into the output array.

    Parameters:
    - rule: Rule object containing rule information
    - appOutY: Array representing the accumulated output

    Returns:
    - updated_appOutY: Updated array representing the accumulated output
    """
    if rule.clipped_consequent is not None:
        # Perform maximum (union) operation between current appOutY and clipped consequent
        updated_appOutY = np.maximum(appOutY, rule.clipped_consequent)
    else:
        raise ValueError("Clipped consequent not defined for the rule")

    return updated_appOutY
