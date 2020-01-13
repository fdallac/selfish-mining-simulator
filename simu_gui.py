# run by typing in terminal:
# bokeh serve --show web_simu.py

from selfishmining import single_selfish_attack_simu, attack_simu_rescaling
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
import time

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, Span
from bokeh.models.widgets import Paragraph, Div
from bokeh.palettes import Spectral6
from bokeh.plotting import figure
from tornado.ioloop import IOLoop

# internal methods

def update_input(attr, old, new):
    global bitcoin_reward, bitcoin_value, D, T, n_steps, time_scale, steps_per_day, q, g, n_days, n_simu
    # update inputs from sliders
    q = q_slider.value
    g = g_slider.value
    n_days = int(t_slider.value)
    n_simu = int(s_slider.value)
    # update time params
    T = 3600 * 24 * n_days
    n_steps = n_days * steps_per_day
    time_scale = np.linspace(0, T, n_days)
    # start new simulation
    simu_and_plot_attacks()


def simu_and_plot_attacks():
    global bitcoin_reward, bitcoin_value, D, T, n_steps, time_scale, steps_per_day, q, g, n_days, n_simu
    # reinitialize vars
    orphans_series = []
    revenues_series = []
    sum_rew_series = np.zeros(n_steps)
    sum_diff_series = np.zeros(n_steps)
    rew_vect_series = []
    diff_vect_series = []
    time_vect_series = []
    win_t_series = []
    # simu
    for n in range(n_simu):
        # simulate attack
        revenue, time_vect, rew_vect, diff_vect, orphans = single_selfish_attack_simu(q, g, D, T, bitcoin_value, bitcoin_reward)
        # rescale time
        rescaled_rew_vect, rescaled_diff_vect = attack_simu_rescaling(rew_vect, diff_vect, time_vect, time_scale)
        # store data arrays
        revenues_series.append(revenue)
        orphans_series.append(orphans)
        rew_vect_series.append(rew_vect)
        diff_vect_series.append(diff_vect)
        time_vect_series.append(time_vect)
        # get starting winning time
        win_t_series.append(get_minimal_winning_time(rescaled_rew_vect))
        # aggregate data 
        sum_rew_series = [(sum_rew_series[i]+rescaled_rew_vect[i]) for i in range(len(sum_rew_series))]
        sum_diff_series = [(sum_diff_series[i]+rescaled_diff_vect[i]) for i in range(len(sum_diff_series))]        
    # compute mean values
    mean_rew_series = [(sum_rew_series[i] / n_simu) for i in range(len(sum_rew_series))]
    mean_diff_series = [(sum_diff_series[i] / n_simu) for i in range(len(sum_diff_series))]
    # update plot data
    source1.data = dict(x=[[t/(3600*24) for t in t_v] for t_v in time_vect_series], y=rew_vect_series)
    source1_1.data = dict(x=[t/(3600*24) for t in time_scale], y=mean_rew_series)
    source1_2.data = dict(x=[0, T/(3600*24)], y=[bitcoin_reward*bitcoin_value*q/600]*2)
    source2.data = dict(x=[[t/(3600*24) for t in t_v] for t_v in time_vect_series], y=diff_vect_series)
    source2_1.data = dict(x=[t/(3600*24) for t in time_scale], y=mean_diff_series)
    hist3, edges3 = np.histogram(win_t_series, density=True, bins=50)
    source3.data = dict(top=hist3, left=edges3[:-1], right=edges3[1:])
    hist4, edges4 = np.histogram(orphans_series, density=True, bins=50)
    source4.data = dict(top=hist4, left=edges4[:-1], right=edges4[1:])
    honest_line.location = bitcoin_reward*bitcoin_value*q/600
    winday_line.location = np.mean(win_t_series)
    orphan_line.location = np.mean(orphans_series)


def get_minimal_winning_time(rew_vect):
    global bitcoin_reward, bitcoin_value, D, T, n_steps, time_scale, steps_per_day, q, g, n_days, n_simu
    
    honest_reward = bitcoin_reward * bitcoin_value * q / 600
    for t in range(len(time_scale)):
        if (rew_vect[t] > honest_reward):
            return np.round(time_scale[t] / (3600 * 24))
    return (n_days + 1)



# initial data
q = 0.30 # attacker hashrate as percentage
g = 0.50 # attacker connection rate
n_days = 90 # simulation time horizon (days)
n_simu = 50 # number of simulations

# constant params
bitcoin_value = 1 # coinbase
bitcoin_reward = 12.5 # n of bitcoin for each block mined
D = 1 # give-up gap (default)

# time params
T = 3600 * 24 * n_days # simulation time horizon (seconds)
steps_per_day = 1
n_steps = n_days * steps_per_day # default --> eventually: n_days*2
time_scale = np.linspace(0, T, n_steps) # time steps array

# vars
orphans_series = []
revenues_series = []
sum_rew_series = np.zeros(n_steps)
sum_diff_series = np.zeros(n_steps)
rew_vect_series = []
diff_vect_series = []
time_vect_series = []
win_t_series = []

# sliders
q_slider = Slider(title='Attacker hashrate (%)',
                value=0.30,
                start=0.00,
                end=0.50,
                step=0.01,
                width=390)
g_slider = Slider(title='Attacker connection rate (%)',
                value=0.50,
                start=0.00,
                end=1.00,
                step=0.01,
                width=390)
t_slider = Slider(title='Time horizon (days)',
                value=90,
                start=0,
                end=365,
                step=1,
                width=390)
s_slider = Slider(title='Number of simulations',
                value=50,
                start=100,
                end=2000,
                step=50,
                width=390)

# setup initial data and layout
source1 = ColumnDataSource(data=dict(x=[], y=[]))
source1_1 = ColumnDataSource(data=dict(x=[], y=[]))
source1_2 = ColumnDataSource(data=dict(x=[], y=[]))
source2 = ColumnDataSource(data=dict(x=[], y=[]))
source2_1 = ColumnDataSource(data=dict(x=[], y=[]))
source3 = ColumnDataSource(data=dict(top=[], left=[], right=[]))
source3_1 = ColumnDataSource(data=dict(x=[], y=[]))
source4 = ColumnDataSource(data=dict(top=[], left=[], right=[]))
source4_1 = ColumnDataSource(data=dict(x=[], y=[]))
honest_line = Span(location=0, dimension='width', line_color='green', line_width=2)
winday_line = Span(location=0, dimension='height', line_color='red', line_width=2.5)
orphan_line = Span(location=0, dimension='height', line_color='red', line_width=2.5)
simu_and_plot_attacks()

# setup plots
label_font_size = '8pt'
p1 = figure(toolbar_location=None, title='Attack reward', width=500, height=300)
p1.xaxis.axis_label, p1.yaxis.axis_label = 'Time horizon [day]', 'Reward [coinbase/time]'
p1.xaxis.axis_label_text_font_style, p1.yaxis.axis_label_text_font_style = 'normal', 'normal'
p1.xaxis.axis_label_text_font_size, p1.yaxis.axis_label_text_font_size = label_font_size, label_font_size
p1.multi_line('x', 'y', source=source1, line_color='black', alpha=0.1)
p1.add_layout(honest_line)
p1.line('x', 'y', source=source1_1, line_color='red', line_width=2.5)
p2 = figure(toolbar_location=None, title='Difficulty adjustment', width=500, height=300)
p2.xaxis.axis_label, p2.yaxis.axis_label = 'Time horizon [day]', 'Difficult factor [#]'
p2.xaxis.axis_label_text_font_style, p2.yaxis.axis_label_text_font_style = 'normal', 'normal'
p2.xaxis.axis_label_text_font_size, p2.yaxis.axis_label_text_font_size = label_font_size, label_font_size
p2.multi_line('x', 'y', source=source2, line_color='black', alpha=0.1)
p2.add_layout(Span(location=1, dimension='width', line_color='green', line_width=2))
p2.line('x', 'y', source=source2_1, line_color='red', line_width=2.5)
p3 = figure(toolbar_location=None, title='Starting winning day', width=300, height=300)
p3.xaxis.axis_label, p3.yaxis.axis_label = 'Time horizon [day]', ''
p3.xaxis.axis_label_text_font_style, p3.yaxis.axis_label_text_font_style = 'normal', 'normal'
p3.xaxis.axis_label_text_font_size, p3.yaxis.axis_label_text_font_size = label_font_size, label_font_size
p3.quad(top='top', bottom=0, left='left', right='right', fill_color='black', line_color='white', alpha=0.8, source=source3)
p3.add_layout(winday_line)
p4 = figure(toolbar_location=None, title='Orphan blocks', width=300, height=300)
p4.xaxis.axis_label, p4.yaxis.axis_label = 'Orphans [#]', ''
p4.xaxis.axis_label_text_font_style, p4.yaxis.axis_label_text_font_style = 'normal', 'normal'
p4.xaxis.axis_label_text_font_size, p4.yaxis.axis_label_text_font_size = label_font_size, label_font_size
p4.quad(top='top', bottom=0, left='left', right='right', fill_color='black', line_color='white', alpha=0.8, source=source4)
p4.add_layout(orphan_line)

# setup interactions
q_slider.on_change('value_throttled', update_input)
g_slider.on_change('value_throttled', update_input)
t_slider.on_change('value_throttled', update_input)
s_slider.on_change('value_throttled', update_input)

# text
txt = Div(text='''<a style="font-size:18px"><b>SELFISH MINING SIMULATOR</b></a><br>
    <p style="font-size:12px">Author: <a href='https://www.linkedin.com/in/filippodallachiara/' target='_blank'>
    Dalla Chiara Filippo</a><br><br>
    This is a simulator of profitability of selfish mining attack against Bitcoin blockchain, built as project for
    Dr Dr. Grunspan Cyril's course "Cryptocurrencies" at ESILV.<br>
    Plots show data of <a style="color:red">simulated selfish mining attack</a> as average of a settable single 
    simulations, against <a style="color:green">theoretical honest strategy</a>.<br><br>
    Selfish mining is a deviant mining strategy, where a major mining operator withholds mined blocks and releases them 
    with a well timed strategy in order to invalidate the maximum number of blocks mined by the rest of the network.<br>
    Profitability of the attack is directly related to reduction of mining difficulty as consequense of slowering down 
    of the network.<br><br>
    Reference: <a href='https://webusers.imj-prg.fr/~ricardo.perez-marco/publications/articles/OnSelfishMining20.pdf' 
    target='_blank'>Grunspan C., Perez R. "On Profitability of Selfish Mining"</a></p>''',
    width=350, height=350)

# layout
inputs = column(txt, q_slider, g_slider, t_slider, s_slider, width=400)
plots = row(column(p1, p2), column(p3, p4))
layout = row(inputs, plots)

# add to document
curdoc().add_root(layout)
curdoc().title = 'Selfish-Mining Simulator'





