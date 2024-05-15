import sys
import skfuzzy as fuzz

sys.path.append('/home/matheus/Documentos/GIT/FuzzyLogicExp/subscriber/src')
from core_functions import logging_pc_changes

setpoint = 2000

"""
This section defines the fuzzy sets to error. 
The error is compute using the difference between the setpoint and the current arrival rate.
"""
# Define fuzzy sets for arrival rate (low, medium, high)
err_low = fuzz.trimf("Error_Low", -1000, -500, 0)
err_med = fuzz.trimf("Error_Medium", -500, 0, 500)
err_high = fuzz.trimf("Error_High", 0, 500, 1000)

# Define fuzzy sets for prefetch count (low, medium, high)
pc_low = fuzz.trimf("PC_Low", 1, 2, 3)
pc_med = fuzz.trimf("PC_Medium", 5, 8, 11)
pc_high = fuzz.trimf("PC_High", 13, 15, 19)

# Define fuzzy sets for PCA (prefetch count adjustment)
pca_low_decrease = fuzz.trimf("PCA_Low_Decrease", -5, -3, -1)
pca_no_change = fuzz.trimf("PCA_No_Change", -2, 0, 2)
pca_low_increase = fuzz.trimf("PCA_Low_Increase", 1, 3, 5)
pca_high_increase = fuzz.trimf("PCA_High_Increase", 4, 6, 8)
pca_high_decrease = fuzz.trimf("PCA_High_Decrease", -8, -6, -4)

# Define fuzzy rules
rule1 = fuzz.rule([err_low, pc_low], pca_high_increase)
rule2 = fuzz.rule([err_low, pc_med], pca_low_increase)
rule3 = fuzz.rule([err_low, pc_high], pca_no_change)
rule4 = fuzz.rule([err_med, pc_low], pca_high_increase)
rule5 = fuzz.rule([err_med, pc_med], pca_no_change)
rule6 = fuzz.rule([err_med, pc_high], pca_low_decrease)
rule7 = fuzz.rule([err_high, pc_low], pca_high_decrease)
rule8 = fuzz.rule([err_high, pc_med], pca_high_decrease)
rule9 = fuzz.rule([err_high, pc_high], pca_low_increase)

# Control system
rule_aggregate = fuzz.ruleblock(
    [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
inference = fuzz.ControlSystem([rule_aggregate])
output = fuzz.FuzzyOutput()

def evaluate_new_prefetch_count(current_prefetch, arrival_rate):
    error = setpoint - arrival_rate
    # Fuzzify inputs
    pc_level = fuzz.interp_membership(fuzz.linguistic_test(
        "PC", current_prefetch), pc_low, pc_med, pc_high)
    err_level = fuzz.interp_membership(fuzz.linguistic_test(
        "Error", error), err_low, err_med, err_high)

    # Evaluate the control system
    output["PCA"] = fuzz.inference(inference, {"PC": pc_level, "Error": err_level})

    # Defuzzify the output (convert to crisp value)
    pca_adjustment = fuzz.defuzzify(output["PCA"], method="centroid")

    # Save logs to file
    logging_pc_changes(arrival_rate, current_prefetch, current_prefetch + pca_adjustment)

    return pca_adjustment
