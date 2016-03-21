from EhealthException import EhealthException


def parse(line):
    try:
        sensor_type, reading = __split_sensor_type(line)
        time, value = __split_value_time(reading)
    except EhealthException as e:
        raise e
    else:
        return (sensor_type, time, value)


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
    except:
        raise EhealthException('Problem Parsing Time Value Pair: ' + reading)
    else:
        return time, value
