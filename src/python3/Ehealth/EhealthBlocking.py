
import time
import argparse
import logging
from EhealthFileHandler import EhealthFileHandler as efh
from EhealthDispatchHandler import EhealthDispatchHandler
from EhealthSerial import EhealthSerial


class EhealthReader:
    def __init__(self, connection, runtime):
        self.connection = connection
        self.runtime = runtime
        self.reponse_handlers = []

    def addResponseHandler(self, handler):
        self.reponse_handlers.append(handler)

    def start(self):
        self.connection.open()
        end_time = self.runtime + time.time()
        while time.time() < end_time:
            try:
                line = self.connection.readline().decode('ascii')
            except Exception as e:
                for handler in self.reponse_handlers:
                    handler.onError(e)
                    logging.warn('Probable Serial Read Error')
            else:
                for handler in self.reponse_handlers:
                    try:
                        handler.onEvent(line)
                    except Exception as e:
                        handler.onError(e)
                        self.reponse_handlers.remove(handler)
        self.connection.close()
        for handler in self.reponse_handlers:
            handler.onStop()


def main():
    parser = argparse.ArgumentParser(
        description="Creates ECG Output File from serial output of Arduino")
    parser.add_argument('port', nargs=1, metavar="Port",
                        help="Port location of the Arduino")
    parser.add_argument('-b', '--baud', nargs=1, metavar='Optional Baud Rate Default (9600)',
                        help="Serial Port Baud Rate (Default 9600)", type=int, default=9600, dest="baud")
    parser.add_argument(
        '-o', '--ouput', nargs=1, metavar="Output file location", default="ecg.txt", dest='output')
    parser.add_argument(
        '-t', '--time', nargs=1, metavar="Number of seconds to run", type=int, default=60, dest='runtime')
    args = parser.parse_args()
    connection = EhealthSerial(args.port[0],9600, 1.5)

    ecgfile = open("ecg.dat", 'w')
    afsfile = open('afs.dat', 'w')
    bpmfile = open('bpm.dat', 'w')
    o2sfile = open('o2s.dat', 'w')

    file_dict = {'ECG': efh(ecgfile), 'AFS': efh(
        afsfile), 'BPM': efh(bpmfile), 'O2S': efh(o2sfile)}

    dispatch = EhealthDispatchHandler(file_dict)

    reader = EhealthReader(connection, args.runtime)
    reader.addResponseHandler(dispatch)
    reader.start()


if __name__ == "__main__":
    main()
