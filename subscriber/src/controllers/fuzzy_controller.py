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
# Error range considers both positive and negative values
error = ctrl.Antecedent(np.arange(-1000, 1001, 1), 'error')
pca = ctrl.Consequent(np.arange(-10, 11, 1), 'pca')

# Define the membership functions for error
error['negative_large'] = fuzz.trimf(error.universe, [-1000, -500, -250])
error['negative_small'] = fuzz.trimf(error.universe, [-500, -250, 0])
error['zero'] = fuzz.trimf(error.universe, [-250, 0, 250])
error['positive_small'] = fuzz.trimf(error.universe, [0, 250, 500])
error['positive_large'] = fuzz.trimf(error.universe, [500, 1000, 1000])

# Define the membership functions for prefetch count adjustment (pca)
pca['low'] = fuzz.trimf(pca.universe, [-10, -5, 0])
pca['medium'] = fuzz.trimf(pca.universe, [-5, 0, 5])
pca['high'] = fuzz.trimf(pca.universe, [0, 5, 10])

# Define the fuzzy rules based on error
rule1 = ctrl.Rule(error['negative_large'], pca['high'])
rule2 = ctrl.Rule(error['negative_small'], pca['medium'])
rule3 = ctrl.Rule(error['zero'], pca['low'])
rule4 = ctrl.Rule(error['positive_small'], pca['low'])
rule5 = ctrl.Rule(error['positive_large'], pca['high'])

# Create the fuzzy system
control_system = ctrl.ControlSystem(
    [rule1, rule2, rule3, rule4, rule5])
controller = ctrl.ControlSystemSimulation(control_system)


def evaluate_new_prefetch_count(current_prefetch, arrival_rate_value):
    # Calculate error as the difference between setpoint and arrival rate
    error_value = setpoint - arrival_rate_value

    # Set input value (error) to the controller
    controller.input['error'] = error_value

    # Compute the output
    controller.compute()

    # Get the output (pca_adjustment)
    pca_adjustment = controller.output['pca']

    # Save logs to file
    logging_pc_changes(arrival_rate_value, current_prefetch,
                       math.ceil(current_prefetch + pca_adjustment))
    sample_saves += 1
    if sample_saves != 1 and sample_saves % 10 == 0:
        setpoint += 250  # Increase the setpoint by 250 messages per second
    return math.ceil(pca_adjustment)
