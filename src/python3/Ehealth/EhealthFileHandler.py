import logging


class EhealthFileHandler:
    def __init__(self, file):
        self.file = file

    def onEvent(self, line):

        try:
            self.file.write(line)
        except Exception as e:
            self.onError(e)
            raise e

    def onError(self, error):
        self.file.close()
        logging.warn('Error in Writing File')

    def onStop(self):
        self.file.close()

    def onStart(self):
    	pass
