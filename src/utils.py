import numpy as np
import math
######################################################################################
def calc_yoy_change(data):
    storePrctDeltas = []
    storeDelta = []
    for i in range(1, len(data)):
        try:
            v1 = data[i - 1]
            v2 = data[i]
            delta = v2 - v1
            # Use absolute value to handle negative denominators correctly
            if v1 != 0:
                prctDelta = (delta / abs(v1)) * 100
            else:
                prctDelta = 0  # or float('inf') or None, depending on how you want to handle div by 0
            storeDelta.append(delta)
            storePrctDeltas.append(prctDelta)
        except:
            continue
    return {"deltas": storeDelta, "prct_deltas": storePrctDeltas}
######################################################################################
def is_nan(value):
    return np.isnan(value)

def is_infinity(value):
    return np.isinf(value)

def check_vals(vals):
    returnVals = []
    for val in vals:
        if is_nan(val):
            val = 0
        elif is_infinity(val):
            val = 0
        returnVals.append(val)
    return returnVals
######################################################################################
def calc_slope(y_values):
    n = len(y_values)
    x_values = list(range(n))
    
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x_squared = sum(x ** 2 for x in x_values)
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = n * sum_x_squared - sum_x ** 2
    
    if denominator == 0:
        return float('inf')
    
    slope = numerator / denominator
    return slope
######################################################################################
def json_serialize(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    else:
        raise TypeError(f"Type {type(obj)} not serializable")
######################################################################################
def flatten_array(x):
    flattened = []
    for i in x:
        if isinstance(i, (np.ndarray, list)):
            if len(i) > 0:
                flattened.append(i[0])
            else:
                flattened.append(0)  # Or float('nan') depending on how you want to handle it
        else:
            flattened.append(i)
    return flattened
######################################################################################