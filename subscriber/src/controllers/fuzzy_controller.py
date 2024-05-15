# Fuzzy library (e.g., scikit-fuzzy)
import skfuzzy as fuzz

setpoint = 2000

# Define fuzzy sets for inputs and output
pc_low = fuzz.trimf("PC_Low", 1, 4, 6)
pc_med = fuzz.trimf("PC_Medium", 9, 11, 13)
pc_high = fuzz.trimf("PC_High", 14, 16, 19)

ar_low = fuzz.trimf("AR_Low", 1000, 1200, 1500)
ar_med = fuzz.trimf("AR_Medium", 1800, 1900, 2100)
ar_high = fuzz.trimf("AR_High", 2400, 2600, 3000)

# Define fuzzy sets for PCA adjustment (decrease and increase)
pca_decrease_large = fuzz.trimf("PCA_Decrease_Large", -15, -13, -11)
pca_decrease_moderate = fuzz.trimf("PCA_Decrease_Moderate", -8, -7, -5)
pca_no_change = fuzz.trimf("PCA_No_Change", -2.5, 0, 2.5)
pca_increase_small = fuzz.trimf("PCA_Increase_Small", 2.5, 4, 6)
pca_increase_moderate = fuzz.trimf("PCA_Increase_Moderate", 8, 10, 12)
pca_increase_high = fuzz.trimf("PCA_Increase_High", 15, 18, 20)

# Fuzzy rules (adapt based on your desired behavior)
rule1 = fuzz.rule(pc_low & ar_low, pca_no_change)
rule2 = fuzz.rule(pc_low & ar_med, pca_increase_moderate)  # Moderate increase
# Higher increase for high arrival rate
rule3 = fuzz.rule(pc_low & ar_high, pca_increase_high)
# More aggressive decrease for low arrival rate
rule4 = fuzz.rule(pc_med & ar_low, pca_decrease_large)
rule5 = fuzz.rule(pc_med & ar_med, pca_no_change)
# Cautious increase for high arrival rate
rule6 = fuzz.rule(pc_med & ar_high, pca_increase_small)
# Aggressive decrease for high prefetch and low arrival
rule7 = fuzz.rule(pc_high & ar_low, pca_decrease_large)
# Moderate decrease for high prefetch and medium arrival
rule8 = fuzz.rule(pc_high & ar_med, pca_decrease_moderate)
rule9 = fuzz.rule(pc_high & ar_high, pca_no_change)

# Control system
rule_aggregate = fuzz.ruleblock(
    [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
inference = fuzz.ControlSystem([rule_aggregate])
output = fuzz.FuzzyOutput()

def evaluate_new_prefetch_count(current_prefetch, arrival_rate):
    # Fuzzify inputs
    pc_level = fuzz.interp_membership(fuzz.linguistic_test(
        "PC", current_prefetch), pc_low, pc_med, pc_high)
    ar_level = fuzz.interp_membership(fuzz.linguistic_test(
        "AR", arrival_rate), ar_low, ar_med, ar_high)

    # Evaluate the control system
    output["PCA"] = fuzz.inference(inference, {"PC": pc_level, "AR": ar_level})

    # Defuzzify the output (convert to crisp value)
    pca_adjustment = fuzz.defuzzify(output["PCA"], method="centroid")

    return pca_adjustment
