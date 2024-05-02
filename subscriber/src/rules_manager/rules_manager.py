import math


def discretize_value(value, bins, parameter):
    normalized_value = value / 5
    max_value = max(data, key=lambda x: x[parameter])[parameter] / 5
    bins_count = len(bins)
    step_size = 1 / (bins_count - 1)
    for i in range(bins_count):
        threshold = i * step_size
        if normalized_value <= threshold:
            return bins[i]
    return bins[-1]

def gaussian_mf(value, c, sigma):
    """
    Source: https://www.mathworks.com/help/fuzzy/gaussmf.html

    The Gaussian MF uses a bell-shaped curve to represent membership.
    This function provides a smoother transition between categories compared to both triangular and trapezoidal MFs. 
    It's defined by a center point (c) and a standard deviation (sigma).
      Args:
          value: The value to evaluate the membership function.
          c: The center point of the curve.
          sigma: The standard deviation of the curve.
      Returns:
          The membership degree of the value.
    """
    return math.exp(-((value - c) ** 2) / (2 * sigma ** 2))

def evaluate_fuzzy_rule(latency_bin, arrival_rate_bin):
    """
    This function evaluates all matching fuzzy rules and returns a list of activation degrees using Gaussian MF.
    Args:
        latency_bin: The discretized bin for latency.
        arrival_rate_bin: The discretized bin for arrival rate.
    Returns:
        A list containing the activation degree for each matching fuzzy rule.
    """
    activation_degrees = []
    for rule in fuzzy_rules:
        if rule["latency_bin"] == latency_bin and rule["arrival_rate_bin"] == arrival_rate_bin:
            low, medium, high = rule["prefetch_count_range"]
            activation_degrees.append(gaussian_mf(
                data[0]["prefetch_count"], (low + high) / 2, (high - low) / 2))
    return activation_degrees

def defuzzify(fuzzy_outputs):
    """
    This function calculates the crisp prefetch count using Center of Gravity (COG) defuzzification.
    Args:
        fuzzy_outputs: A list containing the activation degree for each fuzzy rule.
    Returns:
        The crisp prefetch count based on the COG calculation.
    """
    numerator = 0
    denominator = 0
    prefetch_counts = [data[i]["prefetch_count"]
                       for i in range(len(data))]
    
    # Loop through each rule and its activation degree
    for i, activation in enumerate(fuzzy_outputs):
        if activation == 0:
            continue
        # Calculate weighted sum for numerator (activation * prefetch count)
        numerator += activation * prefetch_counts[i]
        # Calculate total activation for denominator
        denominator += activation

    if denominator == 0:
        return 1  # TODO: Handle this case

    crisp_prefetch_count = numerator / denominator

    return crisp_prefetch_count


# Test the fuzzy system
fuzzy_rules = [
    {"latency_bin": "Low", "arrival_rate_bin": "Low",
        "prefetch_count_range": (1, 2, 3)},
    {"latency_bin": "Low", "arrival_rate_bin": "Medium",
        "prefetch_count_range": (3, 4, 5)},
]
data = [
    {"latency": 10, "arrival_rate": 5, "prefetch_count": 20},
    {"latency": 20, "arrival_rate": 10, "prefetch_count": 25},
]

bins = ["Low", "Medium", "High"]

latency_bin = discretize_value(data[0]["latency"], bins, "latency")
arrival_rate_bin = discretize_value(data[0]["arrival_rate"], bins, "arrival_rate")
fuzzy_outputs = evaluate_fuzzy_rule(latency_bin, arrival_rate_bin)
crisp_prefetch_count = defuzzify(fuzzy_outputs)
print(f"The crisp prefetch count is: {crisp_prefetch_count}")
