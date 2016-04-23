from EhealthConnection import EhealthConnection
from EhealthException import EhealthException
from EhealthCallable import EhealthCallable
import EhealthHandlers
import Ehealthparser
import threading
import time
import logging
from collections import namedtuple
try:
    import Queue as Queue
except:
    import queue as Queue
EhealthEvent = namedtuple('EhealthEvent','event_type msg body')


class Ehealth(EhealthCallable):
    def __init__(self, port, baud):
        EhealthCallable.__init__(self)
        self.__callables = []
        self.__sensor_callables = {}
        self.port = port
        self.baud = baud
        self.connection = EhealthConnection(self.port, self.baud, 3)
        self.__running_lock = threading.Lock()
        self.__run_thread = threading.Thread(target=self.__run,name = 'ehealth')
        self.onErrorCallback = None
        self.__isAlive = False
        self.__messageq = Queue.Queue()

    def start(self):
        try:
            self.connection.open()
            self.__isAlive = True
            self.__run_thread.start()
            self.__messageq.put(EhealthEvent('EhealthStatus','Running','Ehealth is Running'))
        except EhealthException as e:
            raise e

    def stop(self):
        print (self.__run_thread.isAlive())

        if not self.__run_thread.isAlive():
            print (self.__run_thread.isAlive())
            return 
        else:
            print('waiting on lock')
            with self.__running_lock:
                self.__isAlive = False
                print('setting thread closed. is alive:' + str(self.__isAlive))
                self.onStop()
                self.connection.close()
                print('connection closed')
        #try:
        #    self.__running_lock.acquire()
        #    self.__isAlive = False
        #    self.connection.close()
        #    self.onStop()
        #except EhealthException as e:
        #    self.onErrorCallback(e)
        #finally:
        #    self.__running_lock.release()
        #    print('Ehealth has Stopped')

    def isRunning(self):
        with self.__running_lock:
            return self.__isAlive

    def onEvent(self, event):
        if event is not None:
            new_event = Ehealthparser.parse(event)
            if new_event.event_type == 'Reading':
                self.__alert_basic_handler(self.__callables, new_event)
                for sensor_event in new_event.readings:
                    self.__alert_sensor_handler(sensor_event)

    def onError(self, error):
        for handler in self.__callables:
            handler.onError(error)
        for sensor, callable_list in self.__sensor_callables.items():
            for handler in callable_list:
                handler.onError(error)

    def onStop(self):
        for handler in self.__callables:
            handler.onStop()
        for sensor, callable_list in self.__sensor_callables.items():
            for handler in callable_list:
                handler.onStop()

    def __alert_basic_handler(self, callables, event):
        for handler in callables:
            try:
                handler.onEvent(event)
            except Exception as e:
                logging.warn(e + ": Handler Error")
                self.__callables.remove(handler)

    def __alert_sensor_handler(self, event):
        try:
            handler_list = self.__sensor_callables[event.sensor_type]
        except:
            pass
        else:
            self.__alert_basic_handler(handler_list, event)

    def __run(self):
        running = True
        logging.info('Ehealth thread running')
        while running is True:
            with self.__running_lock:
                if self.__isAlive:
                    line = self.connection.readline()
                    if line is not None:
                        self.__handle_response(line)
                running = self.__isAlive
                    #print('exited')
                    #time.sleep(0)
            time.sleep(0)

   


            #try:
            #    self.__running_lock.acquire()
            #    if self.__isAlive:
            #        line = self.connection.readline()
            #        if line is not None:
            #            self.__handle_response(line)
                    #self.onEvent(line)
            #except Exception as e:
            #    logging.error('Ehealth Run error' + str(e))
            #    self.onError(e)
                # self.connection.close()
            #    self.onErrorCallback(e)
            #    self.__isAlive = False
            #finally:
            #    running = self.__isAlive
                #self.__running_lock.release()
        print('Ehealth Finished')
        self.__messageq.put(EhealthEvent('Ehealth','Stopped','Ehealth has Stopped'))
    
    def __handle_response(self,response):
        if response.event_type == 'Exception':
            exception_type = response.msg
            if exception_type == 'SerialException' or exception_type == 'SerialTimeout':
                self.onError(response.body)
                self.onErrorCallback(response.body)
                self.__messageq.put(EhealthEvent('EhealthError','Fatal Error',response.body))
                self.__isAlive = False
                print('is not alive')
        if response.event_type == 'Response':
            self.onEvent(response.body)

    def set_callable(self, *callables):
        for handler in callables:
            if not isinstance(handler, EhealthCallable):
                print(handler)
                raise EhealthException(
                    'Callback Class is not of type EhealthCallable')
            else:
                self.__callables.extend(list(callables))
                print('set callable')
        return self

    def set_onError(self, onError):
        self.onErrorCallback = onError

    def __set_sensor_callable(self, sensor_name, callables):
        for handler in callables:
            print(handler.__class__.__name__)
            if not isinstance(handler, EhealthCallable):
                raise EhealthException(
                    'Callback class is not of type EhealthCallable')
        try:
            call_list = self.__sensor_callables[sensor_name]
        except KeyError:
            self.__sensor_callables[sensor_name] = None

        if self.__sensor_callables[sensor_name] is None:
            self.__sensor_callables[sensor_name] = list(callables)
        else:
            self.__sensor_callables[sensor_name].extend(list(callables))
        return self

    def __send_command(self, command):
        pass

    def register(self, *callbacks,sensor_type = None):
        if sensor_type is None:
            try:
                self.set_callable(*callbacks)
            except:
                raise
        else:
            print(sensor_type)
            try:
                self.__set_sensor_callable(sensor_type, callbacks)
            except:
                raise
    def read_ehealth_message(self):
        try:
            msg = self.__messageq.get(timeout = .1)
        except:
            return None
        else:
            return msg



def onError(error):
    print(error)


def main():
    ehealth = Ehealth('/dev/cu.usbmodem1411', 115200)
    afsfile = EhealthHandlers.filehandler('AFS.dat')
    o2sfile = EhealthHandlers.filehandler('O2S.dat')

    bpmfile = EhealthHandlers.filehandler('BPM.dat')

    ecgfile = EhealthHandlers.filehandler('ECG.dat')

    ehealth.register(afsfile,sensor_type = 'AFS')
    ehealth.register(ecgfile,sensor_type = 'ECG')
    ehealth.register(bpmfile,sensor_type = 'BPM')
    ehealth.register(o2sfile,sensor_type = 'O2S')
    
    ehealth.register(EhealthHandlers.EhealthEchoHandler())
    #ehealth.set_Airflow_callables(afsfile)
    #ehealth.set_ECG_callables(ecgfile)
    #ehealth.set_BPM_callables(bpmfile)
    #ehealth.set_O2S_callables(o2sfile)

    #ehealth.set_callable(EhealthHandlers.EhealthEchoHandler())
    ehealth.set_onError(onError)
    ehealth.start()
    start_time = time.time()
    isRunning = True
    try:
        while time.time() < (start_time + 10) and isRunning:
            msg = ehealth.read_ehealth_message()
            if msg is not None:
                if msg.event_type == 'EhealthError':
                    print(msg.msg)
                    #ehealth.stop()
                    break
                    isRunning = False
                if msg.event_type == "Ehealth":
                    print (msg.msg)
    except KeyboardInterrupt:
        ehealth.stop()
        raise
    print('break')
    ehealth.stop()
    print('finished')
    print(threading.enumerate())
    for t in threading.enumerate():
        print (t.name)
if __name__ == '__main__':
    main()
