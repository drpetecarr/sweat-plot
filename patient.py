import pandas as pd
import numpy as np
from datetime import datetime as dt

import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from session import Session


class Patient:
    def __init__(self, name):
        self.age = None
        self.gender = None
        self.diagnosis = None
        self.name = name
        self.sessions = []
        self.convergence_percentage = None
        self.divergence_percentage = None
        self.total_time = 0
        self.phase_percentages = []
        self.frequency_percentages = []

    def add_session(self, session):
        self.sessions.append(session)
        self.update_percentages()

    def remove_session(self, datetime):
        for s in self.sessions:
            if s.datetime == datetime:
                self.sessions.remove(s)
                self.update_percentages()

    def view_time_graph(self):
        con_bins = [0 for i in range(100)]
        div_bins = [0 for i in range(100)]
        for s in self.sessions:
            percentages_list = s.calculate_con_div(with_con_div=True)
            bc = percentages_list[3]
            dc = percentages_list[4]
            for i, val in enumerate(list(bc)):
                if val == 1:
                    perc = int(np.floor((i / s.time) * 100))
                    con_bins[perc] += 1
            for i, val in enumerate(list(dc)):
                if val == 1:
                    perc_2 = int(np.floor((i / s.time) * 100))
                    div_bins[perc_2] += 1
        plt.figure()
        plt.plot(con_bins, label='CON')
        plt.plot(div_bins, label='DIV')
        plt.legend()
        plt.show()

    def view_session(self, datetime):
        for s in self.sessions:
            if s.datetime == datetime:
                s.view_session()

    def update_percentages(self):
        self.total_time = 0
        cons = 0
        divs = 0
        for s in self.sessions:
            self.total_time += s.time
            cons += int((s.convergence_score / 100) * s.time)
            divs += int((s.divergence_score / 100) * s.time)
        if self.total_time == 0:
            self.convergence_percentage = None
            self.divergence_percentage = None
        else:
            self.convergence_percentage = round((cons / self.total_time) * 100, 4)
            self.divergence_percentage = round((divs / self.total_time) * 100, 4)