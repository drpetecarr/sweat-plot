import sys, os, pickle
from datetime import datetime as dt
from PyQt4 import QtGui, QtCore, uic
from patient import Patient, Session
from patient_category import PatientCategory

ui_file = '/home/ben/PycharmProjects/DadsResearch/main_form.ui'
form, base = uic.loadUiType(ui_file)

PATIENT_DIR = os.path.join(os.getcwd(), 'Patients')


def load_patient_or_cat(name):
    """
    Load patient or patient_category from PATIENT_DIR
    :param name: str
    :return: Patient
    """
    pkl_path = os.path.join(PATIENT_DIR, name + '.pkl')
    if not os.path.exists(pkl_path):
        ValueError("No such " + name + ".pkl file found in " + PATIENT_DIR)
    patient_or_cat = pickle.load(open(pkl_path, "rb"))
    return patient_or_cat


def save_patient_or_cat(patient_or_cat):
    """
    Save patient or category in PATIENT_DIR
    :param patient_or_cat:
    """
    name = patient_or_cat.name
    pkl_path = os.path.join(PATIENT_DIR, name + '.pkl')
    if not os.path.exists(pkl_path):
        ValueError("No such " + name + ".pkl file found in " + PATIENT_DIR)
    pickle.dump(patient_or_cat, open(pkl_path, 'wb'))


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = form()
        self.ui.setupUi(self)

        self.current_patient = None

        self.patient_name = self.ui.patient_combo
        self.patient_name.currentIndexChanged.connect(self.patient_name_changed)

        self.del_patient = self.ui.del_patient
        self.del_patient.clicked.connect(self.del_patient_clicked)
        self.add_patient = self.ui.add_patient
        self.add_patient.clicked.connect(self.add_patient_clicked)
        self.make_category = self.ui.makeCategory
        self.make_category.clicked.connect(self.make_category_clicked)
        self.t = None

        self.number_of_sessions = self.ui.number_of_sessions
        self.convergence_score = self.ui.convergence_score
        self.divergence_score = self.ui.divergence_score

        self.view_date = self.ui.date_combo
        self.view_session_button = self.ui.view_session_button
        self.view_session_button.clicked.connect(self.view_session_clicked)

        self.freq_combo = self.ui.freq_combo
        self.phase_combo = self.ui.phase_combo
        self.add_session_datetime = self.ui.add_session_datetime
        self.add_session_button = self.ui.add_session_button
        self.add_session_button.clicked.connect(self.add_session_clicked)
        self.del_session_button = self.ui.remove_session_button
        self.del_session_button.clicked.connect(self.del_session_clicked)
        self.view_time_dist_button = self.ui.view_time_distribution_button
        self.view_time_dist_button.clicked.connect(self.view_time_clicked)

        self.freq_line_edit = self.ui.frequencies_line_edit
        self.freq_bar_button = self.ui.frequency_bar_button
        self.freq_bar_button.clicked.connect(self.freq_bar_clicked)
        self.freq_table_button = self.ui.frequency_table_button
        self.freq_table_button.clicked.connect(self.freq_table_clicked)

        self.voltages_line_edit = self.ui.voltages_line_edit
        self.phase_bar_button = self.ui.phase_bar_button
        self.phase_bar_button.clicked.connect(self.phase_bar_clicked)
        self.phase_table_button = self.ui.phase_table_button
        self.phase_table_button.clicked.connect(self.phase_table_clicked)

        self.patient_name_changed()
        self.update_patient_list()
        self.update_session_list()

        if not os.path.exists(PATIENT_DIR):
            os.makedirs(PATIENT_DIR)

    def make_category_clicked(self):
        text, ok = QtGui.QInputDialog.getText(self, '', 'Enter category name:')
        if ok:
            new_file_name = os.path.join(PATIENT_DIR, str(text) + '.pkl')
            if os.path.exists(new_file_name):
                QtGui.QMessageBox.about(self, 'Error', 'Name already exists!')
            else:
                self.t = PatientTable(str(text))
                self.t.setGeometry(QtCore.QRect(100, 100, 450, 200))
                self.t.create_table(self.patient_name)
                self.t.create_cat_button()
                self.t.closing.connect(self.update_patient_list)
                self.t.closing.connect(self.update_patient_info)
                self.t.closing.connect(self.update_session_list)
                self.t.show()

    def add_session_clicked(self):
        if self.current_patient is not None:
            file_name = QtGui.QFileDialog.getOpenFileName(self, "Select csv file", '')
            if file_name:
                phse_voltages = []
                freq_voltages = []
                phase_combo = self.phase_combo.currentText()
                freq_combo = self.freq_combo.currentText()
                if phase_combo:
                    phse_voltages = ''.join(phase_combo.split(' ')).split(',')
                    phse_voltages = [float(v) for v in phse_voltages]
                if freq_combo:
                    freq_voltages = ''.join(freq_combo.split(' ')).split(',')
                    freq_voltages = [float(v) for v in freq_voltages]
                self.current_patient.add_session(Session(self.add_session_datetime.dateTime().toPyDateTime(),
                                                         str(file_name), phase_voltages=phse_voltages,
                                                         frequency_voltages=freq_voltages))
                self.update_session_list()
                self.update_patient_info()
                self.save_current_patient()

    def update_session_list(self):
        if self.current_patient is not None:
            if type(self.current_patient) == Patient:
                self.view_date.clear()
                date_list = [s.datetime for s in self.current_patient.sessions]
                for d in date_list:
                    self.view_date.addItem(d.strftime('%d/%m/%y %H:%M:%S'))
            elif type(self.current_patient) == PatientCategory:
                self.view_date.clear()

    def patient_name_changed(self):
        current_patient_name = self.patient_name.currentText()
        if current_patient_name:
            self.current_patient = load_patient_or_cat(current_patient_name)
            self.update_patient_info()
            self.update_session_list()

    def save_current_patient(self):
        if self.current_patient:
            save_patient_or_cat(self.current_patient)

    def update_patient_info(self):
        if type(self.current_patient) == Patient:
            self.convergence_score.setText(str(self.current_patient.convergence_percentage))
            self.divergence_score.setText(str(self.current_patient.divergence_percentage))
            self.number_of_sessions.setText(str(len(self.current_patient.sessions)))
        elif type(self.current_patient) == PatientCategory:
            self.convergence_score.setText('..')
            self.divergence_score.setText('..')
            self.number_of_sessions.setText('..')

    def del_patient_clicked(self):
        p_name = self.patient_name.currentText()
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure you want to delete " + p_name, QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            os.remove(os.path.join(PATIENT_DIR, p_name + '.pkl'))
            self.update_session_list()
            self.update_patient_list()
            self.current_patient = None
        else:
            pass

    def add_patient_clicked(self):
        text, ok = QtGui.QInputDialog.getText(self, '', 'Enter patient name:')
        if ok:
            new_file_name = os.path.join(PATIENT_DIR, str(text) + '.pkl')
            if os.path.exists(new_file_name):
                QtGui.QMessageBox.about(self, 'Error', 'Name already exists!')
            else:
                new_patient = Patient(str(text))
        text, ok = QtGui.QInputDialog.getInt(self, '', 'Enter patient age:')
        if ok:
            new_patient.age = int(text)
        text, ok = QtGui.QInputDialog.getText(self, '', 'Enter patient diagnosis:')
        if ok:
            new_patient.diagnosis = str(text)
        text, ok = QtGui.QInputDialog.getItem(self, '', 'Enter patient gender:', ['Female', 'Male', 'Other'])
        if ok:
            new_patient.gender = str(text)
        pickle.dump(new_patient, open(new_file_name, 'wb'))
        self.update_patient_list()

    def update_patient_list(self):
        self.patient_name.clear()
        patient_list = os.listdir(PATIENT_DIR)
        for p in patient_list:
            p_name = p.split('.')[0]
            self.patient_name.addItem(p_name)

    def view_session_clicked(self):
        datetime = dt.strptime(self.view_date.currentText(), '%d/%m/%y %H:%M:%S')
        self.current_patient.view_session(datetime)

    def del_session_clicked(self):
        datetime = dt.strptime(self.view_date.currentText(), '%d/%m/%y %H:%M:%S')
        self.current_patient.remove_session(datetime)
        self.update_session_list()
        self.save_current_patient()
        self.update_patient_info()

    def view_time_clicked(self):
        if self.current_patient is not None:
            self.current_patient.view_time_graph()

    def freq_bar_clicked(self):
        pass

    def freq_table_clicked(self):
        pass

    def phase_bar_clicked(self):
        pass

    def phase_table_clicked(self):
        pass


class PatientTable(QtGui.QWidget):
    closing = QtCore.pyqtSignal()

    def __init__(self, new_cat_name):
        QtGui.QWidget.__init__(self)
        self._button = None
        self._table = None
        self._new_cat_name = new_cat_name

    def create_cat_button(self):
        self._button = QtGui.QPushButton('Create Category', self)
        self._button.setGeometry(270, 160, 150, 30)
        self._button.clicked.connect(self.create_cat_from_selected_patients)

    def create_cat_from_selected_patients(self):
        patient_names = [item.text() for item in self._table.selectedItems()]
        patients = [load_patient_or_cat(name) for name in patient_names]
        new_cat = PatientCategory(patients, self._new_cat_name)
        save_patient_or_cat(new_cat)
        self.close2()

    def create_table(self, patient_combo_box):
        self._table = QtGui.QTableWidget(self)
        self._table.setColumnCount(1)
        for i in range(patient_combo_box.count()):
            self._table.insertRow(i)
            self._table.setItem(i, 0, QtGui.QTableWidgetItem(patient_combo_box.itemText(i)))

    def close2(self):
        self.closing.emit()
        self.close()

def main():
    app = QtGui.QApplication(sys.argv)
    my_app = MainWindow()
    my_app.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
