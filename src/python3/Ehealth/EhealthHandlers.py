
from EhealthException import EhealthException
from EhealthCallable import EhealthCallable
import logging


class EhealthFileHandler(EhealthCallable):

    def __init__(self, file_n):
        EhealthCallable.__init__(self)
        self.file = file_n

    def onEvent(self, event):
        try:
            self.file.write(event.time + ',' + event.value +'\n')
        except IOError as e:
            self.onError(e)
            raise EhealthException('Could not write to file')

    def onStop(self):
        self.file.close()
        print('closed')

    def onError(self, error):
        self.file.close()
        logging.error(error)
        print('closed')

class EhealthEchoHandler(EhealthCallable):
    def __init__(self):
        EhealthCallable.__init__(self)

    def onEvent(self, event):
        print(event.raw)


def filehandler(file_name):
    try:
        new_file = open(file_name, 'w')
        return EhealthFileHandler(new_file)
    except IOError as e:
        logging.error(e)
        raise e
