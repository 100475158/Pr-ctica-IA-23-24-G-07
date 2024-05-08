import numpy as np
from matplotlib import pyplot as plt
from numpy import var

from MFIS_Read_Functions import *

# Add docstrings to describe the purpose of functions


def main():
    # read files
    inputFuzzySets = readFuzzySetsFile('InputVarSets.txt')
    outputFuzzySets = readFuzzySetsFile('Files/Risks.txt')
    plot_fuzzy_sets(inputFuzzySets)
    plot_output_fuzzy_sets(outputFuzzySets)
    rules = readRulesFile()
    applications = readApplicationsFile()
    inputFuzzySets.printFuzzySetsDict()
    outputFuzzySets.printFuzzySetsDict()
    outputFile = open('Results.txt', "w")
    # process all the applications and write Rests file
    for application in applications:
        centroid = processApplication(
            application, inputFuzzySets, outputFuzzySets, rules)
        outputFile.write(application.appId + " " + str(centroid) + "\n")
    outputFile.close()
    plt.show()

    # Hay que hacer las funciones fuzzify, evaluateAntecedent, evaluateConsequent y la de composition


def processApplication(app, inputFuzzySets, outputFuzzySets, rules):
    # step 1: fuzzification
    fuzzify(app, inputFuzzySets)
    # step 2: inference
    appOutX = np.linspace(0, 100, 1000)
    appOutY = np.zeros_like(outputFuzzySets[list(outputFuzzySets.keys())[0]].y)  # Initialize output array
    for r in rules:
        # step 2.1: compute strength of the antecedent
        evaluateAntecedent(r, inputFuzzySets)
        # step 2.2: clip the consequent
        evaluateConsequent(r, outputFuzzySets)
        # step 2.3: accumulate the output
        appOutY = compose_output(r, appOutY)
    # step 3: defuzzification
    first_output_fuzzy_set = list(outputFuzzySets.values())[0]
    appOutX = first_output_fuzzy_set.x
    centroid = skf.centroid(appOutX, appOutY)
    return centroid


def fuzzify(application, inputFuzzySets):
    for var_value in application.data:
        for setid in inputFuzzySets:
            if inputFuzzySets[setid].var == var:
                inputFuzzySets[setid].memDegree = skf.internp_membership[inputFuzzySets[setid].x,
                                                                         inputFuzzySets[setid].y, var_value]


def evaluateAntecedent(rule, inputFuzzySets):
    rule.strength = 1.0
    for ant in rule.antecedent:
        rule.strength = min(rule.strength, inputFuzzySets[ant].memDegree)


def evaluateConsequent(rule, outputFuzzySets):
    rule.consequentX = outputFuzzySets[rule.consequent].x
    rule.consequentY = outputFuzzySets[rule.consequent].y
    rule.consequentY = np.maximum(rule.consequentY, rule.strength)


def compose_output(rule, appOutY):
    Xnew = np.linspace(0, 100, len(appOutY))
    Xold = np.linspace(0, 100, len(rule.consequentY))
    interpolatedY = np.interp(Xnew, Xold, rule.consequentY)
    return np.maximum(interpolatedY, appOutY)


def plot_fuzzy_sets(fuzzy_sets):
    categorias = set(fs.var for fs in fuzzy_sets.values())

    for categoria in categorias:
        plt.figure(figsize=(8, 4))
        for setid, fs in fuzzy_sets.items():
            if fs.var == categoria:
                plt.plot(fs.x, fs.y, label=f'{fs.label}')
        plt.title(f"Fuzzy Sets for {categoria}")
        plt.xlabel("Universe")
        plt.ylabel("Membership degree")
        plt.legend()
        plt.show()


def plot_output_fuzzy_sets(fuzzy_sets):
    plt.figure(figsize=(8, 4))
    for setid, fs in fuzzy_sets.items():
        plt.plot(fs.x, fs.y, label=f'{fs.label}')
    plt.title("Output Fuzzy Sets")
    plt.xlabel("Universe")
    plt.ylabel("Membership degree")
    plt.legend()
    plt.show()


main()
