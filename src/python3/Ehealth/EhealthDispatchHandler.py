from EhealthException import EhealthException
import Ehealthparser


class EhealthDispatchHandler:
    def __init__(self, file_dict):
        self.dispatch_dict = file_dict

    def onEvent(self, response):

        try:
            event = Ehealthparser.parse(response)
            #sensor_type, time_value, reading_value = parse(response)
        except:
            pass
        else:
            if len(self.dispatch_dict) is not 0:
                try:
                    file_handler = self.dispatch_dict[str(event.sensor_type)]
                    file_handler.onEvent(
                        event.time_value + "," + event.reading_value)
                except EhealthException as e:
                    del self.dispatch_dict[str(event.sensor_type)]
                    raise e
                except KeyError:
                    pass

    def onError(self, error):

        for sensor_type, handler in self.dispatch_dict.items():
            handler.onError(error)

    def onStop(self):

        for sensor_type, handler in self.dispatch_dict.items():
            handler.onStop()

    def onStart(self):
        pass
