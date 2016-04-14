from EhealthConnection import EhealthConnection
from EhealthException import EhealthException
from EhealthCallable import EhealthCallable
import EhealthHandlers
import Ehealthparser
import threading
import time
import logging


class Ehealth(EhealthCallable):
    def __init__(self, port, baud):
        EhealthCallable.__init__(self)
        self.__callables = []
        self.__sensor_callables = {}
        self.port = port
        self.baud = baud
        self.__run_thread = threading.Thread(target=self.__run)
        self.connection = EhealthConnection(self.port, self.baud, 3)
        self.onErrorCallback = None
        self.__running_lock = threading.Lock()
        self.__isAlive = False

    def start(self):
        try:
            self.connection.open()
            self.__isAlive = True
            self.__run_thread.start()
            print('Ehealth is running')
        except EhealthException as e:
            raise e

    def stop(self):
        try:
            print('stopping Ehealth')
            self.__running_lock.acquire()
            self.__isAlive = False
            self.connection.close()
            #logging.info('purging last messages')
            #while True:
            #    try:
            #        line = self.connection.readline()
            #        if line is not None:
            #            self.onEvent(line)
            #    except EhealthException:
            #        break
            self.onStop()
        except EhealthException as e:
            self.onErrorCallback(e)
        finally:
            self.__running_lock.release()
            print('Ehealth has Stopped')
    def isRunning(self):
        with self.__running_lock:
            return self.__isAlive

    def onEvent(self, event):
        if event is not None:
            new_event = Ehealthparser.parse(event)
            if new_event.event_type == 'Reading':
                self.__alert_basic_handler(self.__callables,new_event)
                for sensor_event in new_event.readings:
                    self.__alert_sensor_handler(sensor_event)
            #try:

                #new_event = Ehealthparser.parse(event)
            #except:
                #logging.warn('parse error')
                #pass
            #else:
                #self.__alert_basic_handler(self.__callables, new_event)
                #self.__alert_sensor_handler(new_event)

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
        while running:
            try:
                self.__running_lock.acquire()
                if self.__isAlive:
                    line = self.connection.readline()
                    self.onEvent(line)
            except Exception as e:
                logging.error('Ehealth Run error' + str(e))
                self.onError(e)
                self.connection.close()
                self.onErrorCallback(e)
                self.__isAlive = False
            finally:
                running = self.__isAlive
                self.__running_lock.release()


    def set_BPM_callables(self, *callables):
        try:
            return self.__set_sensor_callable('BPM', callables)
        except EhealthException as e:
            raise e

    def set_ECG_callables(self, *callables):
        try:
            return self.__set_sensor_callable('ECG', callables)
        except EhealthException as e:
            raise e

    def set_O2S_callables(self, *callables):
        try:
            return self.__set_sensor_callable('O2S', callables)
        except EhealthException as e:
            raise e

    def set_Airflow_callables(self, *callables):
        try:
            return self.__set_sensor_callable('AFS', callables)
        except EhealthException as e:
            raise e

    def set_callable(self, *callables):
        for handler in callables:
            if not isinstance(handler, EhealthCallable):
                print(handler)
                raise EhealthException(
                    'Callback Class is not of type EhealthCallable')
            else:
                self.__callables.extend(list(callables))
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


def onError(error):
    raise(error)


def main():
    ehealth = Ehealth('/dev/cu.usbmodem1411', 9600)
    afsfile = EhealthHandlers.filehandler('AFS.dat')
    o2sfile = EhealthHandlers.filehandler('O2S.dat')

    bpmfile = EhealthHandlers.filehandler('BPM.dat')

    ecgfile = EhealthHandlers.filehandler('ECG.dat')

    ehealth.set_Airflow_callables(afsfile)
    ehealth.set_ECG_callables(ecgfile)
    ehealth.set_BPM_callables(bpmfile)
    ehealth.set_O2S_callables(o2sfile)

    ehealth.set_callable(EhealthHandlers.EhealthEchoHandler())
    ehealth.set_onError(onError)
    ehealth.start()
    start_time = time.time()
    while time.time() < (start_time + 20):
        pass
    ehealth.stop()

    pass
if __name__ == '__main__':
    main()
