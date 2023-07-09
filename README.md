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
unpl = xmr.upper_natural_process_limit()
lnpl = xmr.lower_natural_process_limit()
x_bar = xmr.x_average()

url = xmr.upper_range_limit()
mr_bar = xmr.mr_average()

```

Currently, this library only supports the data for generating an XmR chart.
An XmR chart is the simplest type of process behaviour chart.
XmR is short for individual values (X) and a moving range (mR).
More chart data options can be added via pull requests.

For more information, I invite you to read [Making Sense of Data by Donald Wheeler](https://www.amazon.com/Making-Sense-Data-Donald-Wheeler/dp/0945320728).

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
