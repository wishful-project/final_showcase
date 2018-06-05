# -*- coding: utf-8 -*-
import conf
import itertools
import usrp
import time
import numpy as np

from bokeh.models.widgets import Div
from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource
from bokeh.models import NumeralTickFormatter
from bokeh.models.widgets import DataTable
from bokeh.models.widgets import TableColumn
from bokeh.palettes import Colorblind7 as palette
from bokeh.plotting import figure
from bokeh.models import LinearColorMapper, BasicTicker, ColorBar
from bokeh.models.widgets import HTMLTemplateFormatter
from bokeh.models.widgets import DateFormatter
from bokeh.models.widgets import Panel, Tabs
from bokeh.models import Range1d, Plot, LinearAxis, Grid
from bokeh.models.glyphs import ImageURL, Image
from bokeh.plotting import output_file, show
from bokeh.models.widgets import Slider, TextInput

doc = curdoc()
colors = itertools.cycle(palette)
fixed_colors = ["Blue", "Red", "Black", "Orange", "Green", "Purple", "Pink"]

data = dict(name=[], type=[], channel=[], load=[], active=[])
active_networks = ColumnDataSource(data, name='networkStatusUpdate')

nsu_cols = [
    TableColumn(field="name", title="Name", width=120),
    TableColumn(field="type", title="Type", width=120),
    TableColumn(field="channel", title="Channel", width=350),
    TableColumn(field="load", title="Application Load", width=60),
]

# Frequencies : 		2454 		2457 		2459 		2462 		2464 		2467 		2470
# Occurances : 		0 		10 		0 		63 		75 		1 		0
# Bandwidth : 		0 		0.0 		0 		16.0 		5.0 		8.0 		0
data_spec = { "Interference": [], "2454" : [], "2457":[], "2459":[], "2462":[], "2464":[], "2467":[], "2470":[] }
active_spec = ColumnDataSource(data_spec, name='specStatusUpdate')
nsu_cols_spec = [
    TableColumn(field="Interference", title="Interference"),
    TableColumn(field="2454", title="2454"),
    TableColumn(field="2457", title="2457"),
    TableColumn(field="2459", title="2459"),
    TableColumn(field="2462", title="2462"),
    TableColumn(field="2464", title="2464"),
    TableColumn(field="2467", title="2467"),
    TableColumn(field="2470", title="2470"),
]

# {'monitorValue': {'Busy': {'2412': [20, 0.06], '2437': [20, 0.01], '2462': [20, 0.03]}, 'WIFI': {'2412': [20, 0.05], '2437': [20, 0.01], '2462': [20, 0.02]}},
data_spec_2 = { "Interference": [], "2412" : [], "2437":[], "2462":[], "2484":[] }
active_spec_2 = ColumnDataSource(data_spec, name='specStatusUpdate_2')
nsu_cols_spec_2 = [
    TableColumn(field="Interference", title="Interference"),
    TableColumn(field="2412", title="2412"),
    TableColumn(field="2437", title="2437"),
    TableColumn(field="2462", title="2462"),
    TableColumn(field="2484", title="2484"),
]


active_networks_table = DataTable(
    source=active_networks,
    columns=nsu_cols,
    fit_columns=False,
    width=700, height=275
)
tab_table_1 = Panel(child=active_networks_table, title="Networks")
tabs_active_networks_table = Tabs(tabs=[ tab_table_1 ])

spectrum_table = DataTable(
    source=active_spec,
    columns=nsu_cols_spec,
    index_position=None,
    width=600, height=95
)
tab_table_2 = Panel(child=spectrum_table, title="Moitor service")
tabs_spectrum_table = Tabs(tabs=[ tab_table_2 ])

spectrum_table_2 = DataTable(
    source=active_spec_2,
    columns=nsu_cols_spec_2,
    index_position=None,
    width=400, height=95
)
tab_table_3 = Panel(child=spectrum_table_2, title="Moitor service")
tabs_spectrum_table_2 = Tabs(tabs=[ tab_table_3 ])

iframe_text_2 = """<iframe src="http://172.16.16.12/WishfulWebPortal/only_usrp.html" height="350" width="1000" scrolling="no" frameBorder="0" ></iframe>"""
div = Div(text=iframe_text_2, width=900, height=335)

plots = [[
    [div, tabs_spectrum_table],
    [tabs_active_networks_table,  tabs_spectrum_table_2] ]]

master_range = None

plt_array = []
index_color = 0
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
        # color = next(colors)
        # color = next(color_mapper)

        thr_plt.line(
            'timestamp', 'THR',
            source=data, legend=conf.controllers[technology][k]['hrn'],
            line_color=fixed_colors[index_color],
            line_width=3, line_alpha=0.6,
        )
        per_plt.line(
            'timestamp', 'PER',
            source=data, legend=conf.controllers[technology][k]['hrn'],
            line_color=fixed_colors[index_color],
            line_width=3, line_alpha=0.6,
        )
        index_color += 1

    # plots.append([thr_plt, per_plt])
    thr_plt.legend.location = "top_left"
    per_plt.legend.location = "top_left"
    plt_array.append(thr_plt)
    plt_array.append(per_plt)


plots.append([plt_array[0], plt_array[2], plt_array[4], usrp.get_plot('spec_high')])
plots.append([plt_array[1], plt_array[3], plt_array[5], usrp.get_plot('spec_low')])

layout = layout(children=plots, sizing_mode='fixed', name='mainLayout')

doc.add_root(layout)
doc.title = 'WiSHFUL'
