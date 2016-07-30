import pandas as pd
import numpy as np
from datetime import datetime as dt

import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt


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


class Session:
    def __init__(self, datetime, csv_path, phase_voltages=[],
                 frequency_voltages=[]):
        self.datetime = datetime
        self.csv_path = csv_path
        self.phase_voltages = phase_voltages
        self.frequency_voltages = frequency_voltages
        self.raw_data = pd.read_csv(csv_path)
        self.freq_bc_scores = None
        self.phase_bc_scores = None
        self.convergence_score, self.divergence_score, self.time = self.calculate_con_div(with_freq=frequency_voltages,
                                                                                          with_phase=phase_voltages)

    def view_session(self):
        df = self.raw_data
        plt.figure()
        plt.title(self.datetime.strftime('%d/%m/%y') + '  ' + 'CON= ' +
                  str(self.convergence_score) + '  ' + 'DIV= ' +
                  str(self.divergence_score))
        plt.plot(df['Left'], label='Left')
        plt.plot(df['Right'], label='Right')
        plt.legend()
        plt.show()

        if self.phase_bc_scores is not None:
            plt.figure()
            plt.title(self.datetime.strftime('%d/%m/%y') + '  ' + 'CONVERGENCE SCORE FOR DIFFERENT PHASES')
            plt.bar(range(len(self.phase_bc_scores)), self.phase_bc_scores)
            plt.show()
        if self.freq_bc_scores is not None:
            plt.figure()
            plt.title(self.datetime.strftime('%d/%m/%y') + '  ' + 'CONVERGENCE SCORE FOR DIFFERENT FREQUENCIES')
            plt.bar(range(len(self.freq_bc_scores)), self.freq_bc_scores)
            plt.show()

    def calculate_con_div(self, with_con_div=False, with_freq=[], with_phase=[]):
        df = self.raw_data
        time = df['Time']
        left = df['Left']
        right = df['Right']
        if with_freq:
            freq = df['Frequency']
            freq_bc_count = [0] * (len(self.frequency_voltages) + 1)
            freq_band_size = [0] * (len(self.frequency_voltages) + 1)
        if with_phase:
            phase = df['Phase']
            phase_bc_count = [0] * (len(self.phase_voltages) + 1)
            phase_band_size = [0] * (len(self.phase_voltages) + 1)
        bc = np.zeros((len(time), 1))
        dc = np.zeros((len(time), 1))
        for i in range(len(time)):
            if i == 0:
                continue
            if with_phase:
                try:
                    phase_volt = float(phase[i])
                except ValueError:
                    phase_volt = 0
                phase_band = 0
                for k, volt in enumerate(self.phase_voltages):
                    if phase_volt > volt:
                        phase_band = k + 1
                        continue
                    else:
                        break
                phase_band_size[phase_band] += 1
            if with_freq:
                try:
                    freq_volt = float(freq[i])
                except ValueError:
                    freq_volt = 0
                freq_band = 0
                for k, volt in enumerate(self.frequency_voltages):
                    if freq_volt > volt:
                        freq_band = k + 1
                        continue
                    else:
                        break
                freq_band_size[freq_band] += 1
            top = left
            bot = right
            if right[i] > left[i]:
                top, bot = right, left
            if top[i] < top[i - 1]:
                if bot[i] > bot[i - 1]:
                    bc[i] = 1
                    if with_freq:
                        freq_bc_count[freq_band] += 1
                    if with_phase:
                        phase_bc_count[phase_band] += 1
                    continue
            elif top[i] > top[i - 1]:
                if bot[i] < bot[i - 1]:
                    dc[i] = 1
                    continue
        if with_freq:
            self.freq_bc_scores = []
            for k in range(len(freq_band_size)):
                if freq_band_size[k] > 0:
                    self.freq_bc_scores.append(freq_bc_count[k] / freq_band_size[k] * 100)
                else:
                    self.freq_bc_scores.append(0)
        if with_phase:
            self.phase_bc_scores = []
            for k in range(len(phase_band_size)):
                if phase_band_size[k] > 0:
                    self.phase_bc_scores.append(phase_bc_count[k] / phase_band_size[k] * 100)
                else:
                    self.phase_bc_scores.append(0)
        df['bc'] = bc
        df['dc'] = dc
        convergence_percentage = df['bc'].sum() / len(time) * 100
        divergence_percentage = df['dc'].sum() / len(time) * 100
        time = len(time)
        if with_con_div:
            return convergence_percentage, divergence_percentage, time, bc, dc
        return convergence_percentage, divergence_percentage, time

