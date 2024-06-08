import math
from utils.core_functions import logging_pc_changes
import sys
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

sys.path.append('/home/matheus/Documentos/GIT/FuzzyLogicExp/subscriber/src')


class FuzzyController:
    def __init__(self, setpoint=5000):
        self.setpoint = setpoint  # Define setpoint as an attribute
        self.sample_saves = 0
        """
        Define the fuzzy variables and membership functions.
        The error is the input variable, and the prefetch count adjustment (pca) is the output variable.
        """
        self.error = ctrl.Antecedent(np.arange(-100000, 100001, 1), 'error')
        self.pca = ctrl.Consequent(np.arange(-10, 11, 1), 'pca')

        # Define the membership functions for error
        self.error['negative_large'] = fuzz.trimf(self.error.universe, [-10001, -7000, -5000])
        self.error['negative_medium'] = fuzz.trimf(self.error.universe, [-4999, -2500, -1000])
        self.error['negative_small'] = fuzz.trimf(self.error.universe, [-999, -500, -250])
        self.error['zero'] = fuzz.trimf(self.error.universe, [-249, 0, 250])
        self.error['positive_small'] = fuzz.trimf(self.error.universe, [249, 500, 1000])
        self.error['positive_medium'] = fuzz.trimf(self.error.universe, [1001, 2500, 5000])
        self.error['positive_large'] = fuzz.trimf(self.error.universe, [5001, 7000, 10000])

        # Define the membership functions for prefetch count adjustment (pca)
        self.pca['higher_decrease'] = fuzz.trimf(self.pca.universe, [-10, -7, -5])
        self.pca['small_decrease'] = fuzz.trimf(self.pca.universe, [-3, -2, -1])
        self.pca['zero'] = fuzz.trimf(self.pca.universe, [-1, 0, 1])
        self.pca['small_increase'] = fuzz.trimf(self.pca.universe, [1, 2, 3])
        self.pca['higher_increase'] = fuzz.trimf(self.pca.universe, [5, 7, 10])

        # Define the fuzzy rules based on error
        self.rule1 = ctrl.Rule(self.error['negative_large'], self.pca['higher_decrease'])
        self.rule2 = ctrl.Rule(self.error['negative_medium'], self.pca['small_decrease'])  
        self.rule3 = ctrl.Rule(self.error['negative_small'], self.pca['small_decrease'])
        self.rule3 = ctrl.Rule(self.error['zero'], self.pca['zero'])
        self.rule4 = ctrl.Rule(self.error['positive_small'], self.pca['small_increase'])
        self.rule5 = ctrl.Rule(self.error['positive_medium'], self.pca['small_increase'])  
        self.rule6 = ctrl.Rule(self.error['positive_large'], self.pca['higher_increase'])

        # Create the fuzzy system
        self.control_system = ctrl.ControlSystem(
            [self.rule1, self.rule2, self.rule3, self.rule4, self.rule5, self.rule6])
        self.controller = ctrl.ControlSystemSimulation(self.control_system)

    def evaluate_new_prefetch_count(self, current_prefetch, arrival_rate_value):
        """
        The error is the difference between the setpoint and the current value of the arrival rate.
        - If the error is positive, it means that the arrival rate is lower than the setpoint, and PC must be increased.
        - Otherwise, the error negative means that the arrival rate is higher than the setpoint, and PC must be decreased.
        """
        error_value = round(self.setpoint - arrival_rate_value)
        print(f"Error: {error_value}")
        self.controller.input['error'] = error_value
        self.controller.compute()
        pca_adjustment = self.controller.output['pca']

        # Save logs to file
        new_prefetch_count = math.ceil(current_prefetch + pca_adjustment)
        if new_prefetch_count < 1:
            new_prefetch_count = 1
        logging_pc_changes(self.setpoint, arrival_rate_value, error_value, current_prefetch, new_prefetch_count)

        self.sample_saves += 1
        if self.sample_saves != 1 and self.sample_saves % 10 == 0:
            self.setpoint += 250  # Increase the setpoint by 250 messages per second
        return math.ceil(pca_adjustment)
