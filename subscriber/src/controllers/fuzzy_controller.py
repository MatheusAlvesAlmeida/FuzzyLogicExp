import math
from utils.core_functions import logging_pc_changes
import sys
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

sys.path.append('/home/matheus/Documentos/GIT/FuzzyLogicExp/subscriber/src')

setpoint = 500
sample_saves = 0

# Define the fuzzy variables and membership functions
arrival_rate = ctrl.Antecedent(np.arange(0, 2001, 1), 'arrival_rate')
pc = ctrl.Antecedent(np.arange(1, 21, 1), 'pc')
pca = ctrl.Consequent(np.arange(-10, 11, 1), 'pca')

arrival_rate['low'] = fuzz.trimf(arrival_rate.universe, [0, 250, 1000])
arrival_rate['medium'] = fuzz.trimf(arrival_rate.universe, [750, 1750, 2750])
arrival_rate['high'] = fuzz.trimf(arrival_rate.universe, [2250, 3100, 3100])

pc['low'] = fuzz.trimf(pc.universe, [0, 2, 8])
pc['medium'] = fuzz.trimf(pc.universe, [5, 10, 15])
pc['high'] = fuzz.trimf(pc.universe, [12, 18, 20])

# Define the membership functions for prefetch count adjustment (pca)
pca['low'] = fuzz.trimf(pca.universe, [-10, -5, 0])
pca['medium'] = fuzz.trimf(pca.universe, [-5, 0, 5])
pca['high'] = fuzz.trimf(pca.universe, [0, 5, 10])

# Define the fuzzy rules
rule1 = ctrl.Rule(arrival_rate['low'] & pc['low'], pca['high'])
rule2 = ctrl.Rule(arrival_rate['low'] & pc['medium'], pca['medium'])
rule3 = ctrl.Rule(arrival_rate['low'] & pc['high'], pca['low'])
rule4 = ctrl.Rule(arrival_rate['medium'] & pc['low'], pca['high'])
rule5 = ctrl.Rule(arrival_rate['medium'] & pc['medium'], pca['medium'])
rule6 = ctrl.Rule(arrival_rate['medium'] & pc['high'], pca['low'])
rule7 = ctrl.Rule(arrival_rate['high'] & pc['low'], pca['high'])
rule8 = ctrl.Rule(arrival_rate['high'] & pc['medium'], pca['high'])
rule9 = ctrl.Rule(arrival_rate['high'] & pc['high'], pca['low'])

# Create the fuzzy system
control_system = ctrl.ControlSystem(
    [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
controller = ctrl.ControlSystemSimulation(control_system)


def evaluate_new_prefetch_count(current_prefetch, arrival_rate_value):
    # Set input values to the controller
    controller.input['arrival_rate'] = arrival_rate_value
    controller.input['pc'] = current_prefetch

    # Compute the output
    controller.compute()

    # Get the output (pca_adjustment)
    pca_adjustment = controller.output['pca']

    # Save logs to file
    logging_pc_changes(arrival_rate_value, current_prefetch,
                       math.ceil(current_prefetch + pca_adjustment))
    sample_saves += 1
    if sample_saves != 1 and sample_saves % 10 == 0:
        setpoint += 250 # Increase the setpoint by 250 messages per second
    return math.ceil(pca_adjustment)
