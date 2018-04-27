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
from bokeh.models.widgets import CheckboxButtonGroup
from bokeh.plotting import figure
from commander import action_queue

doc = curdoc()
technology_labels = ["LTE", "Wi-Fi", "ZigBee"]


def technology_select(new):
    for x in range(3):
        tech = technology_labels[x].replace("-", "").upper()
        action_queue.put({
            tech: True if x in new else False,
        })


def traffic_select(new):
    for x in range(3):
        tech = technology_labels[x].replace("-", "").upper()
        action_queue.put({
            'TRAFFIC': tech,
        })


def lte_subframe(attr, old, new):
    if attr is not "value":
        return
    action_queue.put({
        "SET_LTE_SUBFRAME_SYNC": new,
    })


def lowpan_blacklist(new):
    channels = [x + 11 for x in new]
    action_queue.put({
        "6LOWPAN_BLACKLIST": channels,
    })


title0 = Div(text="""
    <h2 class="content-subhead">Experiment Control</h2>
    """)
technology_group = CheckboxButtonGroup(
    labels=technology_labels,
    active=[])
technology_group.on_click(technology_select)
traffic_group = CheckboxButtonGroup(
    labels=technology_labels,
    active=[])
traffic_group.on_click(traffic_select)
lowpan_group = CheckboxButtonGroup(
    labels=[str(x) for x in range(11, 27)],
    active=[])
lowpan_group.on_click(lowpan_blacklist)
lte_subframe_slider = Slider(
    start=0, end=50,
    value=10, step=1,
    title='LTE subframe duration',
    callback_policy='mouseup',
    # width=120,
)
lte_subframe_slider.on_change('value', lte_subframe)

controls = layout(
    [
        title0,
        Div(text="""<label>Enable solution</label"""), technology_group,
        Div(text="""<label>Enable traffic</label"""), traffic_group,
        Div(text="""<label>6LOWPAN channel blacklist</label"""), lowpan_group,
        lte_subframe_slider,
    ],
    sizing_mode='scale_width',
)

plots = [[usrp.plot, controls]]
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
        thr_plt.line(
            'timestamp', 'THR',
            source=data, legend=conf.controllers[technology][k]['hrn'],
            line_color=conf.controllers[technology][k]['color'],
            line_width=3, line_alpha=0.6,
        )
        per_plt.line(
            'timestamp', 'PER',
            source=data, legend=conf.controllers[technology][k]['hrn'],
            line_color=conf.controllers[technology][k]['color'],
            line_width=3, line_alpha=0.6,
        )

    plots.append([thr_plt, per_plt])


layout = layout(plots, sizing_mode='scale_width')

doc.add_root(layout)
doc.title = 'WiSHFUL'
