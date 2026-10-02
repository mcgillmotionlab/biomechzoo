SIGNAL ANALYSIS FUNCTIONS
=========================

Functions for computing linear and non-linear signal analysis metrics including impact peaks, loading rate, entropy, smoothness, and
RMS-based measures.

Single-channel metrics
----------------------

Impact Peak
~~~~~~~~~~~

Detects impact peaks in a single time series channel and stores their
frame indices and amplitudes as events.

Loading Rate
~~~~~~~~~~~~

Computes the loading rate (slope around the impact region) for a single
time series channel and stores the result as an event.

Sample Entropy
~~~~~~~~~~~~~~

Calculates the sample entropy of a single time series channel and
stores the value as an event.

Multi-channel metrics
---------------------

Log Dimensionless Jerk (LDLJ)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Computes log dimensionless jerk as a smoothness measure across multiple
channels and stores the resulting value(s) as events.

RMS Ratio (RMSR)
~~~~~~~~~~~~~~~~

Computes the RMS ratio across multiple channels and stores the resulting
value(s) as events.
```
