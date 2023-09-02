# Release History

---

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
