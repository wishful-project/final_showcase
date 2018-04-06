# -*- coding: utf-8 -*-
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
from bokeh.plotting import figure

doc = curdoc()


wifi_thr_plt = figure(
    plot_height=300, plot_width=400,
    title="Wi-Fi Received Data Throughput",
    # tools="crosshair,pan,reset,save,wheel_zoom",
    tools="",
    toolbar_location=None,
    x_axis_type="datetime",
    # y_range=[0, None],
)
wifi_thr_plt.legend.location = "top_left"
wifi_thr_plt.xaxis.axis_label = "Time"
wifi_thr_plt.yaxis.axis_label = "Throughput [B/s]"
wifi_thr_plt.yaxis[0].formatter = NumeralTickFormatter(format='0.0b')
wifi_thr_plt.y_range.start = 0

wifi_per_plt = figure(
    plot_height=300, plot_width=400,
    title="Wi-Fi Performance",
    # tools="crosshair,pan,reset,save,wheel_zoom",
    tools="",
    toolbar_location=None,
    x_axis_type="datetime",
    y_range=[0, 1],
)
wifi_per_plt.legend.location = "top_left"
wifi_per_plt.xaxis.axis_label = "Time"
wifi_per_plt.yaxis.axis_label = "Performance"

for k in conf.wifi_ctrls:
    data = ColumnDataSource(
        data=dict(
            timestamp=[],
            PER=[],
            THR=[],
        ),
        name=k,
    )
    wifi_thr_plt.line(
        'timestamp', 'THR',
        source=data, legend=conf.wifi_ctrls[k]['hrn'],
        line_color=conf.wifi_ctrls[k]['color'],
        line_width=3, line_alpha=0.6,
    )
    wifi_per_plt.line(
        'timestamp', 'PER',
        source=data, legend=conf.wifi_ctrls[k]['hrn'],
        line_color=conf.wifi_ctrls[k]['color'],
        line_width=3, line_alpha=0.6,
    )

title0 = Div(text="""
    <h2 class="content-subhead">Experiment Control</h2>
    """)

controls = layout(
    [
        title0,
    ],
    sizing_mode='scale_width',
)

layout = layout([
    [usrp.plot, controls],
    [wifi_thr_plt, wifi_per_plt],
], sizing_mode='scale_width')

doc.add_root(layout)
doc.title = 'WiSHFUL'
