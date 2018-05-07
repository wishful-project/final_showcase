# -*- coding: utf-8 -*-
import itertools
import conf
import usrp

from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.layouts import layout
from bokeh.layouts import row
from bokeh.layouts import widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models import CustomJS
from bokeh.models import FuncTickFormatter
from bokeh.models import NumeralTickFormatter
from bokeh.models import Title
from bokeh.models import WidgetBox
from bokeh.models.widgets import Div
from bokeh.models.widgets import Slider
from bokeh.models.widgets import Toggle
from bokeh.models.widgets import CheckboxButtonGroup
from bokeh.palettes import Colorblind7 as palette
from bokeh.plotting import figure

doc = curdoc()
colors = itertools.cycle(palette)

plots = [[usrp.get_plot()]]
master_range = None

for technology in conf.controllers:
    thr_plt = figure(
        plot_height=300, plot_width=400,
        title="{} Received Throughput".format(technology),
        # tools="crosshair,pan,reset,save,wheel_zoom",
        tools="",
        toolbar_location=None,
        x_axis_type="datetime",
        # y_range=[0, None],
    )
    thr_plt.legend.location = "top_left"
    thr_plt.xaxis.axis_label = "Time"
    thr_plt.yaxis.axis_label = "Throughput [B/s]"
    thr_plt.yaxis[0].formatter = NumeralTickFormatter(format='0.0b')
    thr_plt.y_range.start = 0

    per_plt = figure(
        plot_height=300, plot_width=400,
        title="{} Performance".format(technology),
        # tools="crosshair,pan,reset,save,wheel_zoom",
        tools="",
        toolbar_location=None,
        x_axis_type="datetime",
        y_range=[0, 1],
    )
    per_plt.legend.location = "top_left"
    per_plt.xaxis.axis_label = "Time"
    per_plt.yaxis.axis_label = "Performance"

    if master_range is None:
        master_range = thr_plt.x_range
    else:
        thr_plt.x_range = master_range
    per_plt.x_range = master_range

    for k in conf.controllers[technology]:
        data = ColumnDataSource(
            data=dict(
                timestamp=[],
                PER=[],
                THR=[],
            ),
            name=k,
        )
        color = next(colors)
        thr_plt.line(
            'timestamp', 'THR',
            source=data, legend=conf.controllers[technology][k]['hrn'],
            line_color=color,
            line_width=3, line_alpha=0.6,
        )
        per_plt.line(
            'timestamp', 'PER',
            source=data, legend=conf.controllers[technology][k]['hrn'],
            line_color=color,
            line_width=3, line_alpha=0.6,
        )

    plots.append([thr_plt, per_plt])


layout = layout(plots, sizing_mode='scale_width')

doc.add_root(layout)
doc.title = 'WiSHFUL'
