from EhealthException import EhealthException
from collections import namedtuple
Event = namedtuple('Event', 'event_type sensor_type time value raw')
Reading = namedtuple('Sensor', 'sensor_type  time value')
Sensor_Event = namedtuple('Event', 'event_type readings time raw')


def parse(line):
    #try:
    #    sensor_type, reading = __split_sensor_type(line)
    #    time, value = __split_value_time(reading)
    #except EhealthException as e:
    #    raise e
    #else:
    #    return Event('Nothing', sensor_type, time, value, line)
    return __new_parse_line(line)


def __split_sensor_type(line):
    try:
        line_split = line.split(":", 1)
        sensor_type = line_split[0]
        reading = line_split[1]
    except:
        raise EhealthException('Problem Parsing Sensor Type Line: ' + line)
    else:
        return sensor_type, reading


def __split_value_time(reading):
    try:
        line_split = reading.split(',', 1)
        time = line_split[0]
        value = line_split[1]
        float(value)
    except:
        raise EhealthException('Problem Parsing Time Value Pair: ' + reading)
    else:
        return time, value


def __new_split_value_time(reading):
    try:
        line_split = reading.split('+')
        time = line_split[0]
        value = line_split[1:]
    except IndexError:
        raise EhealthException('Problem Parsing Time Value Pair: ' + reading)
    else:
        return time, value


def __new_parse_line(line):
    try:
        time, sensor_readings = __new_split_value_time(line)

        new_readings = [
            y for y in [__return_new_reading(time,x) for x in sensor_readings] if y is not None]
        # new_readings = [
           # __return_new_reading(x) for x in sensor_readings if x is not None]
    except EhealthException:
        raise
    else:
        if len(new_readings) == 0:
            return __build_event('Parse Error', new_readings, time, line)
        else:
            return __build_event('Reading', new_readings, time, line)


def __build_event(event_type, readings, time, line):
    return Sensor_Event(event_type, readings, time, line)


def __return_new_reading(time,reading):
    reading_split = reading.split(':')
    try:
        sensor_name = reading_split[0]
        value = reading_split[1]
        float(value)
    except IndexError:
        return None
    except ValueError:
        return None
    else:
        return Reading(sensor_name,time,value)
