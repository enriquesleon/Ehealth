import Ehealth
import EhealthHandlers
import EhealthException
import logging
import EhealthCallable
import argparse
import time


def valid_time(time__string_value):
    value = int(time__string_value)
    print (value)
    if not (value < 0):
        return value
    else:
        raise argparse.ArgumentTypeError(
            'Time Input not valid.' + time__string_value)


def run_ehealth(args):
    eh = Ehealth.Ehealth(args.port[0], 115200)

    if args.all_sensors is True:
        eh.set_callable(EhealthHandlers.EhealthEchoHandler())
        eh.set_Airflow_callables(EhealthHandlers.filehandler('afs.dat'))
        eh.set_BPM_callables(EhealthHandlers.filehandler('bpm.dat'))
        eh.set_ECG_callables(EhealthHandlers.filehandler('ecg.dat'))
        eh.set_O2S_callables(EhealthHandlers.filehandler('o2s.dat'))

    else:
        if args.echo:
            eh.set_callable(EhealthHandlers.EhealthEchoHandler())
        if args.airflow:
            eh.set_Airflow_callables(EhealthHandlers.filehandler('afs.dat'))
        if args.bpm:
            eh.set_BPM_callables(EhealthHandlers.filehandler('bpm.dat'))
        if args.oxy:
            eh.set_O2S_callables(EhealthHandlers.filehandler('o2s.dat'))
        if args.ecg:
            eh.set_ECG_callables(EhealthHandlers.filehandler('ecg.dat'))
    end_time = time.time() + args.runtime[0]
    
    try:
        eh.start()
        end_time = time.time() + args.runtime[0]
        while time.time() < end_time:
            #if not eh.isRunning():
            #	raise EhealthException('Ehealth Error')
            pass
        eh.stop()
    except:
        raise


def main():
    baud = 9600
    parser = argparse.ArgumentParser(
        description="Creates ECG Output File from serial output of Arduino")

    parser.add_argument('--port', nargs=1, metavar="Port",
                        help="Port location of the Arduino", default=['/dev/cu.usbmodem1411'])
    parser.add_argument(
        '-t', '--time', nargs=1, metavar="Runtime", type=valid_time, default=[60], dest='runtime', help='Number of Seconds to run')

    parser.add_argument(
        '-a', '--airflow', action='store_true', default=False, dest='airflow', help="Airflow On")
    parser.add_argument(
        '-p', '--bpm', action='store_true', default=False, dest='bpm', help="BPM On")
    parser.add_argument(
        '-o', '--oxy', action='store_true', default=False, dest='oxy', help='O2 On')
    parser.add_argument(
        '-e', '--ecg', action='store_true', default=False, dest='ecg', help='ECG On')
    parser.add_argument(
        '--all', action='store_true', default=False, dest='all_sensors', help='All Sensor')
    parser.add_argument(
        '--echo', action='store_true', default=False, dest='echo', help='Echo On')
    args = parser.parse_args()
    run_ehealth(args)


if __name__ == "__main__":
    main()
