Ensembler
========================

The Ensembler module provides a flexible framework for constructing
multi-panel biomechanical visualizations from time-series data.

It is built around a modular architecture consisting of:
data loading, plot specification, and pluggable rendering strategies.

Overview
--------

A typical workflow is:

1. Load data via ``Ensembler``
2. Define subplot configurations using ``PlotSpec``
3. Assign rendering strategies (e.g., lines, mean ± SD, events)
4. Build and display the figure

Example
-------

.. code-block:: python

   lines_and_events = CompositeRenderer(
       IndividualLinesRenderer(),
       EventOverlayRenderer()
   )

   ens = Ensembler(
       in_folder=fld,
       channels=channels,
       n_rows=rows,
       n_cols=cols,
       subj_list=subj_list,
       condition_spec=spec
   )

   ens.add_subplot(
       PlotSpec(
           'Right Knee Sagittal plane',
           'Kinemat_x',
           companions=['Angles_x'],
           row=1,
           col=1,
           renderer=IndividualLinesRenderer(),
           x_label='% stance',
           y_label='Joint angle (deg)'
       )
   )

   ens.add_subplot(
       PlotSpec(
           'Right Knee Sagittal plane (mean +/- SD)',
           'Kinemat_x',
           companions=['Angles_x'],
           row=1,
           col=2,
           renderer=MeanSDRenderer(),
           x_label='% stance',
           y_label='Joint angle (deg)'
       )
   )

   fig = ens.build(title='Kinemat vs Plug-in Gait')
   fig.show()

Core Components
---------------

Ensembler
~~~~~~~~~

.. autoclass:: biomechzoo.ensembler.ensembler.Ensembler
   :members:

Plot Specification
~~~~~~~~~~~~~~~~~~

.. autoclass:: biomechzoo.ensembler.plot_spec.PlotSpec
   :members:

Rendering System
----------------

Base renderers define how data is visualized.

.. autoclass:: biomechzoo.ensembler.renderers.IndividualLinesRenderer
   :members:

.. autoclass:: biomechzoo.ensembler.renderers.MeanSDRenderer
   :members:

.. autoclass:: biomechzoo.ensembler.renderers.EventOverlayRenderer
   :members:

.. autoclass:: biomechzoo.ensembler.renderers.CompositeRenderer
   :members:

Data Management
---------------

.. automodule:: biomechzoo.ensembler.data_store
   :members:

Helpers
-------

.. automodule:: biomechzoo.ensembler.helpers
   :members:

Styling
-------

.. automodule:: biomechzoo.ensembler.style_content
   :members: