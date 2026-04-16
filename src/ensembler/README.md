# Biomechoo Ensembler
The plotting environment for the python implementation of biomechZoo
> BiomechZoo for Python available at:
> https://pypi.org/project/biomechzoo/

## Overview
This repository provides the visualization environment for the biomechzoo toolbox implemented in python. The collection
of classes reads .zoo files and, based on user input of channels and events, creates visualizations fit for scientific publications. 

---
## Repository structure 
```
biomechzoo_ensembler/
├── data/
│   └── event_data/               ← Some example data for statistical plots
│   └── line_data/               ← Some example data for line plots
├── src/
│   ├── data_store.py
│   └── ensembler.py
│   ├── helpers.py
│   ├── renderes.py
│   ├── style_content.py
├── main.ipynb                  ← notebook showcasing use cases 
├── main.py                     ← python script with example project
├── ensembler0.0.1.pdf
└── README.md
```

---
## Dependencies
### 1. biomechzoo

The ensembler depends on data being processed with the python implementation of biomechzoo. 


**Setup instructions:**

1. Initialize Python 3.11 for compatibility with https://github.com/stanfordnmbl/opencap-processing
2. Install biomechzoo
```pip install [biomechzoo]```
3. Run biomechzoo pipeline and finish with data normalization ```biomechzoo.normalize(fld)```
4. Initialize the ensembler 

---

## Getting Started
To get started, the Ensembler needs information on: 
1. location of the data ``str``
2. conditions: ```list[str]```, channels: ```list[str]```, and events ```list[str]``` to plot; 
3. subject ids: ```str_match=[r"\b\d{3}[A-Z]{2}\b", r"\b\d{3}[A-Z]{3}\b"]``` OR ```subj_list = list[str]```
4. number of columns and rows.

This information is then used throughout the different assembler classes to extract the relevant data and setup the correct color schemes to plot. 

**Condition specifications**

The Ensembler needs to know if the different conditions (e.g. pre vs post; imu vs vicon) are specified on FOLDER level or on CHANNEL level. 

*Condition set on CHANNEL*

Use case when the condition data is within the same .zoo file flagged by a suffix or prefix. 

```python
spec = ConditionSpec(
    source     = ConditionSource.CHANNEL,
    conditions = ["vicon", "areve", 'pig'],
    channel_map = {
        "vicon": "RS_abduction_vicon",
        "areve": "RS_abduction_areve",
        "pig" : "RS_abduction_pig",
    }
)
```

*Condition set in FOLDER*

Use case when the conditions are separated by different folders in different zoo files with the same name and subject ids

```
biomechzoo_ensembler/
├── data/
│   └── pre/               
│       └── 001JD/
│           └── walk01.zoo
│   └── post/  
│       └── 001JD/
│           └── walk01.zoo

```

```
spec = ConditionSpec(
    source = ConditionSource.FOLDER,
    conditions = ["Pre-surgery", "Post-surgery"]
)
```

**Initializing Ensembler**
```python
ens = Ensembler(in_folder=fld,  channels=channels,
                n_rows=rows,  n_cols=cols,
                str_match=str_match,
                condition_spec=spec,
                events=events)
```

> See the Jupyter notebook or the .pdf for examples to use the full code. 
## Plot options

The following renderers are provided at this moment:

**Line plot options**
1. Individual line plots: ```IndividualLinesRendered()```
2. Average +/- standard deviation of curves: ```MeanSDRenderer()```
3. Adding event data to the individual line plots: ```EventOverlayRenderer()```

**Event plot options**
1. Violin plots to compare groups:  ```ViolinRendered()```
2. Bland-Altman plots for agreement: ```BlandAltmanRendered()```
3. Scatter plots with regression line for correlation: ```ScatterRenderer()```

**Combining**
1. To combine different renderers overlays: ```CompositeRendered()```


All  are called within ```add_subplot(PlotSpec())``` method from the Ensembler class alongside the channel name ,
condition name, row numer, column number and the renderer. 

```python
.add_subplot(PlotSpec(channel = 'RS_abduction', 
                      condition= "vicon", companions=["areve"],
                      row=1, col=1, 
                      renderer=IndividualLinesRenderer()))
```

OR 

```python
.add_subplot(PlotSpec(channel="ax_pelvis_tilt_corr",
        condition = "Pre-surgery", companions = ["Post-surgery"],
        row=1, col=1,
        renderer=ViolinRenderer(),
        events=['impact_peak_mean'],))
```
