import Ehealth
import EhealthHandlers
import EhealthException
import logging
import EhealthCallable
import argparse
import time


def pos_int(int_str):
    try:
        int_str = int(int_str)
    except:
        raise argparse.ArgumentTypeError('Positve integer value required: '+int_str)
    else:
        if not (int_str < 0):
            return int_str
        else:
            raise argparse.ArgumentParser('Positve intger value required ' + int_str)
def valid_time(time__string_value):
    value = int(time__string_value)
    if not (value < 0):
        return value
    else:
        raise argparse.ArgumentTypeError(
            'Time Input not valid.' + time__string_value)

def run_ehealth(args):
    eh = Ehealth.Ehealth(args.port[0], args.baud[0])

    if args.all_sensors is True:
        eh.register(EhealthHandlers.EhealthEchoHandler())
        eh.register(EhealthHandlers.filehandler(args.f[0]+'afs.dat'),sensor_type = 'AFS')
        eh.register(EhealthHandlers.filehandler(args.f[0]+'bpm.dat'),sensor_type='BPM')
        eh.register(EhealthHandlers.filehandler(args.f[0]+'ecg.dat'),sensor_type = 'ECG')
        eh.register(EhealthHandlers.filehandler(args.f[0]+'o2s.dat'),sensor_type = 'O2S')

    else:
        if args.echo:
            eh.set_callable(EhealthHandlers.EhealthEchoHandler())
        if args.airflow:
            eh.set_Airflow_callables(EhealthHandlers.filehandler(args.f[0]+'afs.dat'))
        if args.bpm:
            eh.set_BPM_callables(EhealthHandlers.filehandler(args.f[0]+'bpm.dat'))
        if args.oxy:
            eh.set_O2S_callables(EhealthHandlers.filehandler(args.f[0]+'o2s.dat'))
        if args.ecg:
            eh.set_ECG_callables(EhealthHandlers.filehandler(args.f[0]+'ecg.dat'))
    end_time = time.time() + args.runtime[0]
    
    try:
        eh.start()
    except:
        raise
    end_time = time.time() + args.runtime[0]
    while time.time() < end_time:
        pass
    eh.stop()


def main():
    parser = argparse.ArgumentParser(
        description="Creates ECG Output File from serial output of Arduino")

    parser.add_argument('--port', nargs=1, metavar="Port",
                        help="Port location of the Arduino", default=['/dev/cu.usbmodem1411'])
    parser.add_argument('--baud', nargs=1, metavar = "Baud Rate", help = "Baud Rate", default = [115200],type=pos_int)
    parser.add_argument(
        '-t', '--time', nargs=1, metavar="Runtime", type=valid_time, default=[60], dest='runtime', help='Number of Seconds to run')
    parser.add_argument('-f',metavar = "File Prefix", default = [""], help = "File Prefix")

    parser.add_argument(
        '-a', '--airflow', action='store_true', default=False, dest='airflow', help="Airflow On")
    parser.add_argument(
        '-p', '--bpm', action='store_true', default=False, dest='bpm', help="BPM On")
    parser.add_argument(
        '-o', '--oxy', action='store_true', default=False, dest='oxy', help='O2 On')
    parser.add_argument(
        '-e', '--ecg', action='store_true', default=False, dest='ecg', help='ECG On')
    parser.add_argument(
        '--all', action='store_true', default=False, dest='all_sensors', help='All Sensors')
    parser.add_argument(
        '--echo', action='store_true', default=False, dest='echo', help='Echo On')
    args = parser.parse_args()
    run_ehealth(args)


if __name__ == "__main__":
    main()
