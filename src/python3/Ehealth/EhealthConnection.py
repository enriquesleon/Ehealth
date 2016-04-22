import threading
try:
    import Queue as Queue
except:
    import queue as Queue
import serial
from serial import SerialException
from EhealthException import EhealthException
import logging
import time

from collections import namedtuple
SerialEvent = namedtuple('SerialEvent','event_type msg body')

class EhealthConnection:
    def __init__(self, port, baud, timeout):
        self.port = port
        self.baudrate = baud
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
            self.__connection.baudrate = self.baudrate
            self.__connection.timeout = self.timeout
            self.__connection.open()
            #self.__handshake()
            self.__is_connection_alive = True
            self.__read_thread.start()
            self.__running_event.set()

            print(
                'Serial Connection Open at:' + self.port + ":" + str(self.__connection.baudrate))
            logging.info('Connection Opened')
        except SerialException as e:
            logging.error(e)
            raise EhealthException('Could Not Open Connection')
        except EhealthException as e:
            logging.error(e)
            raise 

    def __run_read(self):
        isRunning = True
        time.sleep(1)
        while isRunning is True:
            self.__running_event.wait()
            try:
                self.__serial_lock.acquire()
                if self.__is_connection_alive:
                    if self.__connection.in_waiting > 0:
                        line = self.__read_line()
                        if line is not None:
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
            logging.warn('Serial Connection Error. Connection not Established')
        else:
            try:
                line = self.__responseq.get(timeout=.1)
            except Queue.Empty:
                logging.info('Queue Empty')
            else:
                return line

    def close(self):
        try:
            self.__serial_lock.acquire()
            self.__connection.close()
            self.__is_connection_alive = False
        except:
            raise EhealthConnection('Could not close Connection')
        finally:
            pass
            self.__serial_lock.release()

    def pause(self):
        self.__running_event.clear()

    def __read_line(self):
        try:
            serial_line = self.__connection.readline()
            line = serial_line.decode('ascii')
        except Exception as e:
            raise EhealthException('Couldnt decode Bytes' + serial_line.decode('hex'))        
        return line
    def __handshake(self):
        while (not (self.__connection.in_waiting > 0)):
            pass
        try:
            time.sleep(.5)
            cts = self.__connection.read(1).decode('ascii')
            if cts != 'c':
                raise EhealthException
            print (cts)
            self.__connection.write('o'.encode('ascii'))
        except:
            raise EhealthException('Could not Hanshake')


def main():
    connection = EhealthConnection('/dev/cu.usbmodem1411', 115200, 1)
    try:
        connection.open()
    except EhealthException as e:
        print(e)
        raise
    while True:
        try:
            line = connection.readline()
            if line is not None:
                print(line)
        except EhealthException as e:
            print(e)
            connection.close()
            raise
        except KeyboardInterrupt:
            connection.close()
            raise
if __name__ == '__main__':
    main()
