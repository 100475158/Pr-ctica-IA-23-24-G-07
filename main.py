
from matplotlib import pyplot as plt
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
    outputFile = open('Results.txt', "w")
    # process all the applications and write Rests file
    for application in applications:
        centroid = processApplication(
            application, inputFuzzySets, outputFuzzySets, rules)
        outputFile.write(application.appId + " " + str(centroid) + "\n")
    outputFile.close()
    inputFuzzySets.printFuzzySetsDict()
    outputFuzzySets.printFuzzySetsDict()
    plt.show()

    # Hay que hacer las funciones fuzzify, evaluateAntecedent, evaluateConsequent y la de composition


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
        appOutY = compose_output(r, appOutY)
    # step 3: defuzzification
    first_output_fuzzy_set = list(outputFuzzySets.values())[0]
    appOutX = first_output_fuzzy_set.x
    centroid = skf.centroid(appOutX, appOutY)
    return centroid


def fuzzify(application, inputFuzzySets):
    for var_value in application.data:
        for setid in inputFuzzySets:
            if inputFuzzySets[setid].var == var_value[0]:
                inputFuzzySets[setid].memDegree = np.interp(var_value[1],inputFuzzySets[setid].x, inputFuzzySets[setid].y)
def evaluateAntecedent(rule, inputFuzzySets):
    rule.strength = 1
    for ant in rule.antecedent:
        rule.strength = min(rule.strength, inputFuzzySets[ant].memDegree)


def evaluateConsequent(rule, outputFuzzySets):
    rule.consequentX = outputFuzzySets[rule.consequent].x
    rule.consequentY = outputFuzzySets[rule.consequent].y
    rule.consequentY = np.minimum(rule.consequentY, rule.strength)


def compose_output(rule, appOutY):
    return np.maximum(rule.consequentY, appOutY)


def plot_fuzzy_sets(fuzzy_sets):
    categorias = set(fs.var for fs in fuzzy_sets.values())
    num_categorias = len(categorias)

    # Calcular número de filas y columnas para los subplots
    num_cols = 3  # Número de columnas en la disposición de subplots
    num_rows = (num_categorias + num_cols - 1) // num_cols  # Calcula el número de filas

    # Crear una figura grande con subplots
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 5 * num_rows))
    axes = axes.flatten()  # Aplanar el arreglo de subplots en una sola lista

    for i, categoria in enumerate(categorias):
        ax = axes[i]  # Seleccionar el subplot actual
        for setid, fs in fuzzy_sets.items():
            if fs.var == categoria:
                ax.plot(fs.x, fs.y, label=f'{fs.label}')
        ax.set_title(f"Fuzzy Sets for {categoria}")
        ax.set_xlabel("Universe")
        ax.set_ylabel("Membership degree")
        ax.legend()

    # Ocultar subplots no utilizados
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    # Ajustar automáticamente el diseño y mostrar la figura
    fig.tight_layout()
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
