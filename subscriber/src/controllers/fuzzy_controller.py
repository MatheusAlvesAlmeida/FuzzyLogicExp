import math
from utils.core_functions import logging_pc_changes
import sys
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

sys.path.append('/home/matheus/Documentos/GIT/FuzzyLogicExp/subscriber/src')


class FuzzyController:
    def __init__(self, setpoint=500):
        self.setpoint = setpoint  # Define setpoint as an attribute
        self.sample_saves = 0
        # Define the fuzzy variables and membership functions
        self.error = ctrl.Antecedent(np.arange(-1000, 1001, 1), 'error')
        self.pca = ctrl.Consequent(np.arange(-10, 11, 1), 'pca')

        # Define the membership functions for error
        self.error['negative_large'] = fuzz.trimf(
            self.error.universe, [-1000, -500, -250])
        self.error['negative_small'] = fuzz.trimf(
            self.error.universe, [-500, -250, 0])
        self.error['zero'] = fuzz.trimf(self.error.universe, [-250, 0, 250])
        self.error['positive_small'] = fuzz.trimf(
            self.error.universe, [0, 250, 500])
        self.error['positive_large'] = fuzz.trimf(
            self.error.universe, [500, 1000, 1000])

        # Define the membership functions for prefetch count adjustment (pca)
        self.pca['low'] = fuzz.trimf(self.pca.universe, [-10, -5, 0])
        self.pca['medium'] = fuzz.trimf(self.pca.universe, [-5, 0, 5])
        self.pca['high'] = fuzz.trimf(self.pca.universe, [0, 5, 10])

        # Define the fuzzy rules based on error
        self.rule1 = ctrl.Rule(self.error['negative_large'], self.pca['high'])
        self.rule2 = ctrl.Rule(
            self.error['negative_small'], self.pca['medium'])
        self.rule3 = ctrl.Rule(self.error['zero'], self.pca['low'])
        self.rule4 = ctrl.Rule(self.error['positive_small'], self.pca['low'])
        self.rule5 = ctrl.Rule(self.error['positive_large'], self.pca['high'])

        # Create the fuzzy system
        self.control_system = ctrl.ControlSystem(
            [self.rule1, self.rule2, self.rule3, self.rule4, self.rule5])
        self.controller = ctrl.ControlSystemSimulation(self.control_system)

    def evaluate_new_prefetch_count(self, current_prefetch, arrival_rate_value):
        # Calculate error as the difference between setpoint and arrival rate
        error_value = round(self.setpoint - arrival_rate_value)
        self.controller.input['error'] = error_value
        self.controller.compute()
        pca_adjustment = self.controller.output['pca']

        # Save logs to file
        logging_pc_changes(self.setpoint, error_value, current_prefetch,
                           math.ceil(current_prefetch + pca_adjustment))

        self.sample_saves += 1
        if self.sample_saves != 1 and self.sample_saves % 10 == 0:
            self.setpoint += 250  # Increase the setpoint by 250 messages per second
        return math.ceil(pca_adjustment)
