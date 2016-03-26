import logging


class EhealthFileHandler:
    def __init__(self, file_n):
        self.file_n = file_n

    def onEvent(self, line):

        try:
            self.file_n.write(line)
        except Exception as e:
            self.onError(e)
            raise e

    def onError(self, error):
        self.file_n.close()
        logging.warn('Error in Writing File')

    def onStop(self):
        print('closed')
        self.file_n.close()
        logging.warn('file closed')

    def onStart(self):
    	pass
