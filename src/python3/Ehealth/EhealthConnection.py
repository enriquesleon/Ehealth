import threading
try:
    import Queue as Queue
except:
    import queue as Queue
import serial
from serial import SerialException
from EhealthException import EhealthException
import logging


class EhealthConnection:
    def __init__(self, port, baud, timeout):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.__connection = serial.Serial()
        self.__read_thread = threading.Thread(target=self.__run_read)
        self.__serial_lock = threading.Lock()
        self.__responseq = Queue.Queue()
        self.__running_event = threading.Event()
        self.__is_connection_alive = False

    def open(self):
        try:
            self.__connection.port = self.port
            self.__connection.baud = self.port
            self.__connection.timeout = self.timeout
            self.__connection.open()
            self.__is_connection_alive = True
            self.__read_thread.start()
            print('connection open')
        except SerialException as e:
            logging.error(e)
            raise EhealthException('Could Not Open Connection')

    def __run_read(self):
        isRunning = True
        while isRunning is True:
            try:
                self.__serial_lock.acquire()
                if self.__is_connection_alive:
                    line = self.__connection.readline().decode('ascii')
                    self.__responseq.put(line)
            except SerialException:
                self.__connection.close()
                logging.error('Serial Read Error')
                self.__is_connection_alive = False
            except Queue.Full:
                logging.warning('Queue Full')
                pass
            finally:
                isRunning = self.__is_connection_alive
                self.__serial_lock.release()

    def readline(self):

        if self.__responseq.empty() and not self.__read_thread.is_alive():
            raise EhealthException('Serial Read Error')
        else:
            try:
                line = self.__responseq.get(timeout=1)
            except Queue.Empty:
                pass
                #raise EhealthException('Serial Read Error')
            else:
                return line

    def close(self):
        try:
            self.__serial_lock.acquire()
            self.__connection.close()
            self.__is_connection_alive = False
        except:
            raise EhealthConnection('Could not close Connection')


def main():
    connection = EhealthConnection('/dev/cu.usbmodem1411', 9600, 1)
    try:
        connection.open()
    except EhealthException as e:
        print(e)
        raise
    while True:
        try:
            print(connection.readline())
        except EhealthException as e:
            print(e)
            connection.close()
            raise
        except KeyboardInterrupt:
            connection.close()
            raise
if __name__ == '__main__':
    main()

