import threading
try:
    import Queue as Queue
except:
    import queue as Queue
import serial
from serial import SerialException
from serial import SerialTimeoutException
from EhealthException import EhealthException
import logging
import time

from collections import namedtuple
SerialEvent = namedtuple('SerialEvent','event_type msg body')
CommandEvent = namedtuple('CommandEvent','command_type msg')

class EhealthConnection:
    def __init__(self, port, baud, timeout):
        self.port = port
        self.baudrate = baud
        self.timeout = timeout
        self.__connection = serial.Serial()
        self.__read_thread = threading.Thread(target=self.__run_read,name = 'serial')
        self.__serial_lock = threading.Lock()
        self.__responseq = Queue.Queue()
        self.__running_event = threading.Event()
        self.__is_connection_alive = False
        self.__commandq = Queue.Queue()

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
                if not self.__commandq.empty():
                    self.__command_handler()
                else:
                    self.__read_into_queue()
                #if self.__is_connection_alive:
                #    if self.__connection.in_waiting > 0:
                #        line = self.__read_line()
                #        if line is not None:
                #            self.__responseq.put(line)
            except SerialException as e:
                self.__serial_exception_handler(e)
            except SerialTimeoutException as e:
                self.__serial_exception_handler(e)
            except UnicodeDecodeError as e:
                self.__serial_exception_handler(e)
                #self.__connection.close()
                #logging.error('Serial Read Error')
                #self.__is_connection_alive = False
            #except Queue.Full:
                #logging.warning('Queue Full')
                #pass
            finally:
                isRunning = self.__is_connection_alive
                self.__serial_lock.release()
                time.sleep(0)
        print('serial finished')
    def __command_handler(self):
        command = self.__commandq.get()
        if command.command_type == "Stop":
            self.__connection.close()
            self.__is_connection_alive = False

    def __read_into_queue(self):
        if self.__is_connection_alive:
            try:
                line = self.__read_line()
                if line is not None:
                    self.__responseq.put(SerialEvent('Response','New Response',line))
            except:
                raise
    def __serial_exception_handler(self,e):
        te = type(e)
        if te is SerialException:
            #self.__connection.close()
            logging.error('Serial Read Error')
            self.__is_connection_alive = False
            self.__responseq.put(SerialEvent('Exception','SerialException',e))
        if te is SerialTimeoutException:
            logging.error('Serial Timeout')
            self.__responseq.put(SerialEvent('Exception','SerialTimeout',e))
        if te is UnicodeDecodeError:
            logging.error('Could not decode Bytes')
            self.__responseq.put(SerialEvent('Exception','DecodeException',e))
        if te is Queue.Full:
            logging.error('Queue is Full')
            self.__responseq.put('Exception','QueueFull',e)

    def readline(self):

        #if self.__responseq.empty() and not self.__read_thread.is_alive():
            #raise EhealthException('Serial Read Error')
            #logging.warn('Serial Connection Error. Connection not Established')
        #else:
        #    try:
        #        line = self.__responseq.get(timeout=.1)
        #    except Queue.Empty:
        #        logging.info('Queue Empty')
        #    else:
        #        return line
        try:
            line = self.__responseq.get(timeout = .1)
        except Queue.Empty:
            logging.info('Queue Empty')
            return None
        else:
            return line



    def close(self):
        self.__commandq.put(CommandEvent('Stop','Normal Stop'))
        #try:
        #    self.__serial_lock.acquire()
        #    self.__connection.close()
        #    self.__is_connection_alive = False
        #except:
        #    raise EhealthConnection('Could not close Connection')
        #finally:
        #    self.__serial_lock.release()

    def pause(self):
        self.__running_event.clear()

    def __read_line(self):
        try:
            serial_line = self.__connection.readline()
            line = serial_line.decode('ascii')
        except SerialException:
            raise 
        except SerialTimeoutException:
            raise
        except UnicodeDecodeError:
            raise       
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
    
    while True:
        try:
            line = connection.readline()
            if line is not None:
                if line.event_type == 'Exception':
                    print(line.msg)
                    #raise line.body
                    break
                if line.event_type == 'Response':
                    print (line.body)
        except KeyboardInterrupt:
            connection.close()


    #while True:
    #    try:
    #        line = connection.readline()
    #       if line is not None:
    #            if line.event_type is 'Exception':
    #                print('Exception')
    #                break
    #                #raise line.body
    #           else:
    #                print(line.body)
    #    except EhealthException as e:
    #        print(e)
    #        connection.close()
    #    except KeyboardInterrupt:
    #        connection.close()
    #        raise
if __name__ == '__main__':
    main()
