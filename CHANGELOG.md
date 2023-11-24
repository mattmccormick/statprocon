# Release History

---

## 1.0.0

- Public release
- Raise exception if less than 2 counts are provided

## 0.9.0

- Add `x_exponential_moving_average()` method to return exponential moving averages
- Add optional `include_exponential_moving_averages` flag to `to_dict()` to allow including the values in the returned dict
- Add support for Python 3.12
- Drop support for end of life Python 3.7

## 0.8.0

- Add `x_plot()` and `mr_plot()` methods to plot more detailed charts using `pandas` and `matplotlib` that highlight any data points that meet the detection rules

## 0.7.0

- Switch `limit_floor` parameter to constructor rather than passing through different methods

## 0.6.0

- Add helper method `is_lnpl_above_floor()` to check if the Lower Natural Process Limit has any value that is above the specified floor argument.  This can be used to check if LNPL should be used or not
- Add optional parameter `lower_natural_process_limit_floor` to `x_to_dict()` method.  If the LNPL is not above this value, it will not be included in the result
- Remove optional `floor` parameter from `lower_natural_process_limit()`.  The helper method can be used to check if this condition occurs

## 0.5.1

- Rename `moving_average()` to `x_moving_average()`

## 0.5.0

- Add optional `moving_average_points` parameter to `to_dict()` and `x_to_dict()` to return moving average values for the number of points

## 0.4.0

- Add optional `floor` parameter to `lower_natural_process_limit()` to allow specifying a value that LNPL cannot be more negative than

## 0.3.0

- Add optional `include_halfway_lines` parameter to `to_dict()` and `x_to_dict()` to return halfway lines that should capture 85% of X values in predictable processes  

## 0.2.0

- Add `XmRTrending()` class to compute trending X central line and natural process limits

## 0.1.1

- Add parameter `x_central_line_uses` to accept `median` and return the median for the X central line

## 0.1.0

- Add parameter `moving_range_uses` to accept `median` and compute the limits using the median moving range

## 0.0.10

- Change minimum required Python version to 3.7

## 0.0.9

- Change return type of central_line and limits methods to return a list instead of a scalar value

## 0.0.8

- Standardize `to_dict` keys
- All keys return same length for easy import to `pandas`
- Add `x_to_dict()` and `mr_to_dict()` methods

## 0.0.7

- Accept `float` inputs
- Add `to_csv()` method

## 0.0.6

- Round averages to 3 digits to match limits
- Add `to_dict()` and implement `__repr()__`

## 0.0.5

- Fix bug with point equal to limits being detected

## 0.0.4

- Support type hints

## 0.0.2

- Add optional ability to restrict limit calculations to a subset of the count data

## 0.0.1

- Added XmR chart based on the average moving range
