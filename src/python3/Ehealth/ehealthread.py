import serial
import time
import threading
import argparse
import logging
import sys


class EhealthWriteHandler:
    def __init__(self, file):
        self.file = file

    def onResonse(self, reponse):
        try:
            self.file.write(reponse)
        except Exception as e:
            print("error writing")
            raise

    def onStop(self):
        self.file.close()

    def onError(self, error):
        print (error)
        self.file.close()


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
                raise
            else:
                for handler in self.reponse_handlers:
                    try:
                        handler.onResonse(line)
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

    connection = serial.Serial()
    connection.port = args.port[0]
    connection.baud = args.baud[0]
    connection.timeout = 1.5

    out = open(args.output, 'w')
    handler = EhealthWriteHandler(out)
    reader = EhealthReader(connection,args.runtime[0])
    reader.addResponseHandler(handler)
    reader.start()




if __name__ == "__main__":
    main()
