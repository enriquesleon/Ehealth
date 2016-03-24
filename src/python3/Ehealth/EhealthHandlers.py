
from EhealthException import EhealthException
from EhealthCallable import EhealthCallable


class EhealthFileHandler(EhealthCallable):

    def __init__(self, file):
        EhealthCallable.__init__(self)
        self.file = file

    def onEvent(self, event):
        try:
            self.file.write(event.time + ',' + event.value)
        except IOError as e:
            self.onError(e)
            raise EhealthException('Could not write to file')

    def onStop(self):
        self.file.close()

    def onError(self, error):
        self.file.close()

class EhealthEchoHandler(EhealthCallable):
    def __init__(self):
        EhealthCallable.__init__(self)

    def onEvent(self, event):
        print(event.raw)


def filehandler(file_name):
    try:
        file = open(file_name, 'w')
        return EhealthFileHandler(file)
    except IOError as e:
        raise e
