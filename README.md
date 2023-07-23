# statprocon

**statprocon** is a Python helper library for generating data for use in **Stat**istical **Pro**cess **Con**trol charts.
SPC charts are also known as Process Behaviour Charts, Control charts or Shewhart charts.

## Installation

```shell
pip install statprocon
```

## Usage

```python
from statprocon import XmR

counts = [10, 50, 40, 30]

xmr = XmR(counts)
moving_ranges = xmr.moving_ranges()
unpl = xmr.upper_natural_process_limit()[0]  # 85.7
lnpl = xmr.lower_natural_process_limit()[0]  # -20.7
x_cl = xmr.x_central_line()[0]  # 32.5

url = xmr.upper_range_limit()[0]  # 65.36
mr_cl = xmr.mr_central_line()[0]  # 20

```

Currently, this library only supports the data for generating an XmR chart.
An XmR chart is the simplest type of process behaviour chart.
XmR is short for individual values (X) and a moving range (mR).
More chart data options can be added via pull requests.

For more information, please read [Making Sense of Data by Donald Wheeler](https://www.amazon.com/Making-Sense-Data-Donald-Wheeler/dp/0945320728).

### pandas

Visualize XmR charts using Jupyter Notebooks and [pandas](https://pandas.pydata.org/)

```python
import pandas as pd
from statprocon import XmR

xmr = XmR(counts)

pd.DataFrame(xmr.x_to_dict()).astype(float).plot()
pd.DataFrame(xmr.mr_to_dict()).astype(float).plot()
```

![Screenshot from 2023-07-22 13-53-22](https://github.com/mattmccormick/statprocon/assets/436801/b6a83903-4bb9-4935-9acb-c086d3420fd2)


### CSV

Generate a CSV of all the data needed to create XmR charts.

```python
print(xmr.to_csv())
```

### Google Sheets Charts

Generate XmR Charts in Google Sheets

https://github.com/mattmccormick/statprocon/assets/436801/0de1a9f3-a8ad-4047-8c9d-0f890e0bf453

1. Make a copy of the [statprocon XmR Template sheet](https://docs.google.com/spreadsheets/d/1IdCBpE8FK4qP8B7qHQeXX6amLZ8oyhc8OjlBlGHmWTg/edit?usp=sharing)
1. Paste the CSV output from above into cell A1
1. Click `Data -> Split Text to Columns`

The X and MR charts will appear on the right.

Note that the Lower Natural Process Limit may not make sense if your count data could not possibly go negative.
If LNPL is not needed, remove it with the following steps:

1. Double-click on the X Chart
1. Click the `Setup` tab
1. Under `Series`, find `LNPL`
1. Click the 3 dot menu on the right next to `LNPL`
1. Click `Remove`

The LNPL line will be removed from the X Chart.

## Advanced Usage

### Calculate Limits from Subset of Counts

The central lines and limits calculations can be restricted to a subset of the count data.
Use the `subset_start_index` and `subset_end_index` parameters when instantiating the XmR object:

```python
xmr = XmR(counts, subset_start_index=10, subset_end_index=34)  # 24 points of data starting at index 10
```

When one or both of these optional arguments are provided, the the X and MR central line calculations will be modified to only use the data from `subset_start_index` up to, but not including, `subset_end_index`.
When these optional arguments are not provided, `subset_start_index` defaults to 0 and `subset_end_index` defaults to the length of `counts`.

## Dependencies

There are a few other Python libraries for generating SPC charts but they all contain large dependencies in order to include the ability to graph the chart.
This package will remain small and light and not require large dependencies.
The user will need to convert the data into charts on their own.

This package also contains extensive tests for verifying the integrity of the calculated data.

---
## Development

Create virtualenv

```shell
python3 -m venv venv
```

Activate virtualenv

```shell
source venv/bin/activate
```

[Build](https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archiveshttps://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives)

```shell
python -m build
```

[Upload](https://packaging.python.org/en/latest/tutorials/packaging-projects/#uploading-the-distribution-archives)

```shell
python -m twine upload dist/*
```

### Testing

[Install package from source](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#installing-from-source)
```shell
python3 -m pip install .
```

Run tests
```shell
python3 -m unittest discover
```
