import pandas as pd
import numpy as np
from datetime import datetime as dt
import matplotlib

matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt


class PatientCategory:
    def __init__(self, patients, name):
        self.patients = patients
        self.name = name
        self.average_age = np.mean([p.age for p in self.patients])

    def average_con(self):
        count = 0
        running_sum = 0
        for p in self.patients:
            if p.convergence_percentage is not None:
                running_sum += p.convergence_percentage
                count += 1
        if count == 0:
            return None
        return running_sum / count

    def average_div(self):
        count = 0
        running_sum = 0
        for p in self.patients:
            if p.divergence_percentage is not None:
                running_sum += p.divergence_percentage
                count += 1
        if count == 0:
            return None
        return running_sum / count

    def add_patients(self, patients):
        self.patients += patients

    def view_time_graph(self):
        con_bins = [0 for i in range(100)]
        div_bins = [0 for i in range(100)]
        for p in self.patients:
            for s in p.sessions:
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
