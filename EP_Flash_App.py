from Augury_EP_Flash_UI import *
import asyncio
from qasync import QEventLoop, asyncSlot
import os
from PyQt5.QtCore import QProcess
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

from Alineedit import FileEdit

# print to gui

# def message(self, s):
#     self.cmd_textEdit.appendPlainText(s)



class FlashApp(Ui_MainWindow):
    def __init__(self, window):
        super().__init__()
        # init all the ui file -> todo : show shaked
        self.setupUi(window)
        self.p = None
        self.bat_lot_Flash_cond = ""

        #  todo : show shaked - from here all component is ready for you !
        #  todo : here we in the main win
        print("App init Start Run ...")

        # global var
        ############
        fw_path = ""
        self.flash_done = False
        self.stage = 0

        #line edit validator
        ####################
        self.SN_lineEdit.setInputMask("0000000000")             # validator input
        self.BATlot_lineEdit.setInputMask("000000000")           # validator input

        # call back event
        #################
        self.Flash_Pb.clicked.connect(self.start_flash)         # Start Flash
        self.Clear_Pb.clicked.connect(self.clear_console)             # delete console
        self.SN_lineEdit.textChanged.connect(self.sn_callback)  # SN change call back
        self.FWpath_lineEdit.textChanged.connect(self.Fw_path_callback) # todo: debbig only
        # init state
        self.SN_lineEdit.setFocus()


        # define Process to run Shell cmd
        #################################
        #self.process = QProcess()
        # Connect the readyReadStandardOutput signal to the handle_output method
        #self.process.readyReadStandardOutput.connect(self.handle_output)
        # Start the external command
        # Note: cmd /c is used to execute the command and then terminate the cmd process
        #self.process.start("shell", ["/c", "ls"])
        print("App init Run Ok ")

    def console_print(self, str):
        self.plainTextEdit.appendPlainText(str)
        #self.cmd_textEdit.append(str)


    def message(self, s):
        self.plainTextEdit.appendPlainText(s)
        #self.cmd_textEdit.appendPlainText(s)

    # only if SN is valid next to bat / or finish
    def sn_callback(self):
        serial = self.SN_lineEdit.text()  # we take from ui to logic var serial
        print(serial)
        if (len(serial) == 10):
            self.console_print("SN - is valid")
            #self.BATlot_lineEdit.setDisabled(False)  todo: arnon
            self.BATlot_lineEdit.setFocus()
            #self.BATlot_lineEdit.setText('')  # for arno add number  todo: arnon
            print("sn_callback finish ")
        else:
            #self.BATlot_lineEdit.setDisabled(True) todo: arnon
            pass

    def Fw_path_callback (self):
        print("Fw_path_callback")

    def handle_output(self):
        print("handle_output")
        # Read the standard output of the process
        data = self.process.readAllStandardOutput()
        # Decode the bytes to string and append it to the text area
        output = bytes(data).decode("utf-8")
        self.cmd_textEdit.appendPlainText(output)

    def start_flash(self):
        #print("start flash EP")
        #self.process.start("python3", ["dummy_script.py"])

        self.console_print( "**************")
        self.console_print( "start flash EP")
        self.console_print( "**************")

        #1. data ready
        ##############
        # get all the data is ok
        serial_str   = self.SN_lineEdit.text()
        bat_lot_str  = self.BATlot_lineEdit.text()
        Fw_path  = self.FWpath_lineEdit.text()


        # 2. data valid
        ###############
        if (len(serial_str) <8 ):
            print("Error in SN length ")
            self.SN_lineEdit.clear()
            self.SN_lineEdit.setFocus()
            return

        if Fw_path == "":
            print("Need insert Path")
            return

        if Fw_path[-4:].upper() != ".HEX":
            print("you must add only Hex file ")
            return

        #option for dev  / must for arnon todo: arnonmode
        if bat_lot_str == "":
            self.bat_lot_Flash_cond = False
            print("not need to flash")
        else:
            self.bat_lot_Flash_cond = True
            print("must need to flash")


        # 3. start burn by condition
        ############################
        print("Valid data is ok ")
        self.console_print( "SN  NUM ---- >"+ serial_str)
        self.console_print( "BAT LOT ---- >"+ bat_lot_str)
        self.console_print( "--------------")

        # 4. prepare to shell cmd format
        ################################
        try:
            #convert str to int Serial
            serial_int = int(serial_str)
            serial_hex = (hex(serial_int))
            self.ser_towriteA = serial_hex[3:]
            self.ser_towriteB = serial_hex[2]


            if (self.bat_lot_Flash_cond):
                print("bat lot will burn")
                print(self.bat_lot_Flash_cond)
                bat_int = int(bat_lot_str)
                self.Bat_towrite = bat_int
        except :
            print("data for shell error - stage 4   ")
            return

        # 5. burn process !
        ###################
        # cmd to do
        self.start_process()

    def start_process(self):
        print("--- start_process Shell ---")
        print(self.p)
        self.flash_error = False
        if self.p is None:  # No process running.
            self.console_print("Executing process to flush ")
            self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.p.readyReadStandardOutput.connect(self.handle_stdout) # read out put
            self.p.readyReadStandardError.connect(self.handle_stderr)  # read Error
            self.p.stateChanged.connect(self.handle_state)             # State change
            self.p.finished.connect(self.process_finished)  # Clean up once complete.
            cmd = (
                'nrfjprog --program ~/Downloads/merged_15G.hex --verify --chiperase && nrfjprog --reset')
                #Example valid path : Users/asztrozenberg/Downloads/merged_15G.hex
                #Example valid path : ~/Downloads/merged_canary_r4000_high_g_rev_a_0.1.09.0003+7730.hex

            #cmd = ('nrfjprog -v')
            # for run script from file in....  here
            #self.p.start("python3", ['dummy_script.py'])
            #self.p.(cmd)
            self.p.start("sh", ["-c" , cmd])
            self.p.waitForFinished()
            #self.p.start("sh", ["-c", cmd])
            print("finish shell process")

            #5A . Serial number
            string1 = 'nrfjprog --memwr 0x10001080 --val 0x'
            string1 = string1 + self.ser_towriteA
            self.message(string1)
            print(string1)

            string2 = 'nrfjprog --memwr 0x10001088 --val 0x'
            string2 = string2 + self.ser_towriteB
            self.message(string2)
            print(string2)

            print(" -------   serial number 1 ")
            self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.p.readyReadStandardOutput.connect(self.handle_stdout)  # read out put
            self.p.readyReadStandardError.connect(self.handle_stderr)  # read Error
            self.p.stateChanged.connect(self.handle_state)  # State change
            self.p.finished.connect(self.process_finished)
            self.p.start("sh", ["-c", string1])
            self.p.waitForFinished()

            print(" -------   serial number 2 ")
            self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.p.readyReadStandardOutput.connect(self.handle_stdout)  # read out put
            self.p.readyReadStandardError.connect(self.handle_stderr)  # read Error
            self.p.stateChanged.connect(self.handle_state)  # State change
            self.p.finished.connect(self.process_finished)
            self.p.start("sh", ["-c", string2])
            self.p.waitForFinished()

            if (self.bat_lot_Flash_cond):
                print("======================    bat_lot_Flash_cond   =====================")
                string3 = 'nrfjprog --memwr 0x1000108c --val '
                string3 = string3 + str(int(self.Bat_towrite))
                print(string3)
                self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
                self.p.readyReadStandardOutput.connect(self.handle_stdout)  # read out put
                self.p.readyReadStandardError.connect(self.handle_stderr)  # read Error
                self.p.stateChanged.connect(self.handle_state)  # State change
                self.p.finished.connect(self.process_finished)
                self.p.start("sh", ["-c", string3])
                self.p.waitForFinished()

            if self.flash_error :
                print("error")
            else :
                print("++++++++++++++++++++++++++++++++++")
                print("+++++++++++   Done    ++++++++++++")
                print("++++++++++++++++++++++++++++++++++")
            #self.p.start("sh", ["/c", "ls"])

    # call back from shell
    def handle_stderr(self):
        print("handle_stderr")
        self.flash_error = True
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.console_print(self, stderr)
        print(stderr)


    def handle_stdout(self):
        print("handle_stdout")
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        print(data)
        self.console_print(stdout)


    def handle_state(self, state):
        print("handle_state")
        states = {
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.console_print(f"State changed: {state_name}")

    def process_finished(self):
        self.console_print("Process finished.")
        self.stage = 3
        self.p = None


    # process is until here !!!

    def clear_console(self):
        print("clear console")
        self.cmd_textEdit.setText("")


def main():
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    MainWindow = QtWidgets.QMainWindow()
    ui = FlashApp(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
