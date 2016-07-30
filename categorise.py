import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np


def categorise(csv_path):
    """
    Takes in csv with left and right skin resistance readings. Looks for instances where both readings are vertically
    travelling in different directions but are converging, i.e., the rate of change of the upper reading is downwards
    and the rate of change of the lower reading is upwards. We will call this bidirectional convergence (bc).

    Saves a csv which is a copy of the input only with another column, flagging all instance of bc with a 1.

    :param csv_path: str
    """
    df = pd.read_csv(csv_path)
    time = df['Time']
    left = df['Left']
    right = df['Right']
    bc = np.zeros((len(time), 1))
    for i in range(len(time)):
        if i == 0:
            continue
        top = left
        bot = right
        if right[i] > left[i]:
            top, bot = right, left
        if top[i] < top[i-1]:
            if bot[i] > bot[i-1]:
                bc[i] = 1
                continue
    print(len(time))
    df['bc'] = bc
    score = df['bc'].sum() / len(time) * 100
    pd.DataFrame.to_csv(df, csv_path.replace('.csv', '_with_bc_' + str(score) + '.csv'))

categorise('/home/ben/PycharmProjects/DadsResearch/AG64 EMDR6 Spreadsheet1.csv')