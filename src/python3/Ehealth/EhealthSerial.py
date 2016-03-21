import serial
from EhealthException import EhealthException
from serial import SerialException


class EhealthSerial:

    def __init__(self, port, baud, timeout):

        self.__connection = serial.Serial()
        self.__connection.port = port
        self.__connection.baud = baud
        self.__connection.timeout = timeout

    def open(self):

        try:
            self.__connection.open()
            self.__connection.readline()
            print('Connection Open')
        except Exception as e:
            raise EhealthException('Serial Connection Error. Could Not Open')

    def readline(self):

        try:
            line = self.__connection.readline()
        except SerialException as e:
            raise EhealthException('Serial Read Error')
        else:
            return line

    def write(self, line):

        try:
            self.__connection.write(line.encode('ascii'))
        except Exception as e:
            raise EhealthException('Serial Write Error')

    def close(self):

        self.__connection.close()
