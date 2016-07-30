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

    def add_patients(self, patients):
        self.patients += patients