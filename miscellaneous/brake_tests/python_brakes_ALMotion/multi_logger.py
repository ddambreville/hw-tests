#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2014/01/06
Last modification 2014/03/12

@author: Emmanuel NALEPA
@contact: enalepa[at]aldebaran-robotics.com
@copyright: Aldebaran Robotics 2014

@requires:  - naoqi python SDK  (Available on Version Gate)
              for logging from ALMemory

            - usbtc08.dll and picolog_tc08_manager.py for logging from
              Picolog TC08
              (Available with git clone
              git@git.aldebaran.lan:test-nao/picolog_tc08_python_driver.git)

            - PicoHRDL.dll and picolog_adc24_manager.py for logging from
              Picolog ADC24
              (Available with git clone
              git@git.aldebaran.lan:test-nao/picolog_adc24_python_driver.git)

@platform : - Windows, Linux (PC or robot), OS X
            - If use of TC08 or/and ADC24, only Windows

@summary: This module permits to log datas from several sources
@source availables : ALMemory, Picolog TC08 and Picolog ADC24

@known issues : - For TC08, in the configuration file, you have to put channels
                  in order (1, 2 .. 8)
                - For ADC24, in the configuration file, you have to put
                  channels in order (1, 2, ...., 16).
                - You cannot choose the order of probe in the log file

@pep8 : Complains without rules R0902, R0912, R0913, R0914, R0915 and W0212
@version : 2
"""

import sys
import time
import argparse
import ConfigParser
import threading

DEFAULT_CONFIG_FILE = "multi_logger.cfg"
DEFAULT_PERIOD = 1
DEFAULT_OUTPUT = "Console"
DEFAULT_DECIMAL = 2
DEFAULT_IP = "127.0.0.1"

LOGGERS_CONFIG_FILE = "probs_config.cfg"


class Logger(object):

    """
        Logger class
        This class permits to log datas from several sources
    """

    def __init__(self, robotIP, configFilePath=DEFAULT_CONFIG_FILE,
                 samplePeriod=DEFAULT_PERIOD, output=DEFAULT_OUTPUT,
                 decimal=DEFAULT_DECIMAL):
        """
            Initialize the logger.
            - robotIP : IP adress of the robot
              (Examples : "bn10.local" or "127.0.0.1")
            - configFilePath (optional) : Path of the configuration file
            - samplePeriod (optional) : Sample period
            - output (optional) : Output where results will be written
            - decimal (optional) : Number of decimal for the Time variable
        """

        self.robotIP = robotIP
        self.configFilePath = configFilePath
        self.samplePeriod = samplePeriod
        self.output = output
        self.decimal = decimal
        self.configFileDic = self._readConfigFile(self.configFilePath)
        self.loggersConfigfileDic = self._readConfigFile(LOGGERS_CONFIG_FILE)
        self.hasToLog = True

        if output != "Console":
            try:
                self.logFile = open(output, "w")
            except IOError:
                print "ERROR : File", output, "cannot be oppened."
                sys.exit()

        # Initialize ALMemory
        if "ALMemory" in self.configFileDic.keys():
            from naoqi import ALProxy
            self.mem = ALProxy("ALMemory", robotIP, 9559)

        # Initialize TC08 if need to do it
        if "TC08" in self.configFileDic.keys():
            import picolog_tc08_manager

            if "TC08" not in self.loggersConfigfileDic.keys():
                print "multi_logger.py ERROR : You want to use TC08 " + \
                    "logger but there is no section for it in probs_config.cfg"
                sys.exit()

            dicTc08 = self.loggersConfigfileDic["TC08"]

            if "NoiseRejection" not in dicTc08.keys():
                print "multi_logger.py ERROR : Key \"NoiseRejection\" has " + \
                    " to be in the \"TC08\" section of \"probs_config.cfg\"."
                sys.exit()

            noiseRejectionTc08 = dicTc08["NoiseRejection"][0]

            # Opening module
            sys.stdout.write("TC08 : Opening module ... ")
            sys.stdout.flush()
            self.tc08 = picolog_tc08_manager.ModuleTc08()
            sys.stdout.write("OK\n")

            # Setting noise rejection
            sys.stdout.write("TC08 : Setting noise rejection module ... ")
            sys.stdout.flush()
            self.tc08.setMains(noiseRejectionTc08)
            sys.stdout.write("OK\n")

            # Enabling channels
            sys.stdout.write("TC08 : Setting channels ... ")
            sys.stdout.flush()
            for channelConfig in self.configFileDic["TC08"].values():
                (channel, thermoCoupleType) = channelConfig

                self.tc08.setChannel(int(channel), thermoCoupleType)

            sys.stdout.write("OK\n")

            # Getting minimum sampling interval
            sys.stdout.write("TC08 : Gettint minimum sampling interval ... ")
            sys.stdout.flush()
            minimumSamplingInterval = self.tc08.getMinimumIntervalMs()
            sys.stdout.write("OK\n")

            # Start logging on TC08
            sys.stdout.write("TC08 : Run ... ")
            sys.stdout.flush()
            self.tc08.run(minimumSamplingInterval)
            sys.stdout.write("OK\n")

        # Initialize ADC24 if need to do it
        if "ADC24" in self.configFileDic.keys():
            import picolog_adc24_manager

            if "ADC24" not in self.loggersConfigfileDic.keys():
                print "multi_logger.py ERROR : You want to use ADC24 " + \
                    "logger but there is no section for it in probs_config.cfg"
                sys.exit()

            dicAdc24 = self.loggersConfigfileDic["ADC24"]

            if "NoiseRejection" not in dicAdc24.keys():
                print "multi_logger.py ERROR : Key \"NoiseRejection\" has " + \
                    " to be in the \"ADC24\" section of \"probs_config.cfg\"."
                sys.exit()

            if "ConversionTime" not in dicAdc24.keys():
                print "multi_logger.py ERROR : Key \"ConversionTime\" has " + \
                    " to be in the \"ADC24\" section of \"probs_config.cfg\"."
                sys.exit()

            noiseRejectionAdc24 = dicAdc24["NoiseRejection"][0]
            conversionTime = dicAdc24["ConversionTime"][0]

            # Opening module
            sys.stdout.write("ADC24 : Opening module ... ")
            sys.stdout.flush()
            self.adc24 = picolog_adc24_manager.ModuleAdc24()
            sys.stdout.write("OK\n")

            # Setting noise rejection
            sys.stdout.write("ADC24 : Setting noise rejection module ... ")
            sys.stdout.flush()
            self.adc24.setMains(noiseRejectionAdc24)
            sys.stdout.write("OK\n")

            # Enabling channels
            sys.stdout.write("ADC24 : Setting channels ... ")
            sys.stdout.flush()
            for channelConfig in self.configFileDic["ADC24"].values():
                (channel, voltageRange, end) = channelConfig

                self.adc24.enableAnalogInChannel(int(channel), voltageRange,
                                                 end)
            sys.stdout.write("OK\n")

            # Setting intervals (in SetInterval, periods are set in
            # milli-seconds)
            sys.stdout.write("ADC24 : Setting intervals ... ")
            sys.stdout.flush()
            self.adc24.setInterval(int(samplePeriod * 1000), conversionTime)

            sys.stdout.write("OK\n")

            # Start logging on ADC24 (1 sample for each channel at a time,
            # windowed mode)
            sys.stdout.write("ADC24 : Run ... ")
            sys.stdout.flush()
            self.adc24.run(1, "BM_WINDOW")

            sys.stdout.write("OK\n")

            # Waiting ADC24 is ready
            sys.stdout.write("ADC24 : Wait ready ... ")
            sys.stdout.flush()
            while not self.adc24.isReady():
                pass

            sys.stdout.write("OK\n")

        headers = ["Time"]
        for probe in self.configFileDic.values():
            for key in probe.keys():
                headers.append(key)

        toWrite = ", ".join(headers).replace(" ", "")

        if output == "Console":
            print toWrite
        else:
            print "Logging ..."
            self.logFile.write(toWrite + "\n")

        self.t0 = time.time()

    @classmethod
    def _listConfigFileSections(cls, configFilePaths):
        """List all the sections of the probs_config file <configFilePaths>"""
        probsConfig = ConfigParser.ConfigParser()
        probsConfig.optionxform = str
        probsConfig.read(configFilePaths)

        return probsConfig.sections()

    @classmethod
    def _readConfigFileSection(cls, configFilePath, section):
        """
            Use ConfigParser for reading a configuration file.
            Returns an dictionnary with keys/values of the section.
        """

        probsConfig = ConfigParser.ConfigParser()
        probsConfig.optionxform = str
        probsConfig.read(configFilePath)

        if probsConfig.has_section(section):
            configSection = probsConfig._sections[section]
            configSection.pop("__name__")

            for key, value in configSection.items():
                configSection[key] = value.split()

            return configSection

        else:
            return {}

    def _readConfigFile(self, configFilePath):
        """ Return the dictionnary corresponding to the configuration file."""
        dic = {}
        for section in self._listConfigFileSections(configFilePath):
            dic[section] = self._readConfigFileSection(configFilePath, section)

        return dic

    def log1Line(self):
        """Write 1 log line output in file or console."""

        elapsedTime = time.time() - self.t0
        elapsedTimeRound = round(elapsedTime, self.decimal)

        values = [elapsedTimeRound]

        for probe, dicToLog in self.configFileDic.items():
            if probe == "ALMemory":
                alMemoryKeys = ["".join(memoryValue)
                                for memoryValue in dicToLog.values()]
                values += self.mem.getListData(alMemoryKeys)

            if probe == "TC08":
                tc08ValuesDic = self.tc08.getValues()
                values += [value for value in tc08ValuesDic.values()]

            if probe == "ADC24":
                adc24ValuesDic = self.adc24.getValues()
                values += [value[0] for value in adc24ValuesDic.values()]

        toWrite = str(values).strip('[]').replace(" ", "")

        if self.output == "Console":
            print toWrite
        else:
            self.logFile.write(toWrite + "\n")

    # def log(self):
    #     """
    #         Log in file or console.
    #         Use a threding timer calling itself. If you have a better idea
    #         to have a periodically not drifting sampling, I am interrested
    #         in !
    #     """
    #     def myTimer(period):
    #         """Define the timer which let to log periodically."""
    #         threading.Timer(period, myTimer, [period]).start()
    #         self.log1Line()

    #     myTimer(self.samplePeriod)

    def log(self):
        """Log in file or console."""

        # This function uses a sleep.
        # I tried to use a threding timer calling itself(only way I know on
        # Python to do a periodically timer). It works fine, but with this way
        # we can't catch a Keyboard interrupt and stop properly picologgers ...
        # For the timer implementation, just see "log" above ...

        def loop(period):
            """Log 1 line and sleep during a period"""
            while self.hasToLog is True:
                self.log1Line()
                time.sleep(period)

        logThread = threading.Thread(target=loop, args=(self.samplePeriod,))
        logThread.daemon = True
        logThread.start()

    def stop(self):
        """Stop logging."""
        self.hasToLog = False

        # This dirty sleep is necessary to allow time to the thread to exit
        # before the main program
        time.sleep(1)


def main():
    """Read the configuration file and start logging."""
    parser = argparse.ArgumentParser(description="Log datas from ALMemory")

    parser.add_argument("-i", "--IP", dest="robotIP", default=DEFAULT_IP,
                        help="Robot IP or name (default: 127.0.0.1)")

    parser.add_argument("-c", "--configFile", dest="configFile",
                        default=DEFAULT_CONFIG_FILE,
                        help="configuration log file\
                        (default: multi_logger.cfg)")

    parser.add_argument("-p", "--period", dest="period", type=float,
                        default=DEFAULT_PERIOD,
                        help="sampling period in seconds (default: 1 sec)")

    parser.add_argument("-o", "--output", dest="output",
                        default=DEFAULT_OUTPUT,
                        help="output file or console (default: Console)")

    parser.add_argument("-d", "--decimal", dest="decimal", type=int,
                        default=DEFAULT_DECIMAL,
                        help="number of decimals for time (default: 2)")

    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s 2.0")

    args = parser.parse_args()

    logger = Logger(
        args.robotIP, args.configFile, args.period, args.output,
        args.decimal)

    logger.log()

    # Continue if the user hit "Enter"
    # Do nothing specially in case of KeyboardInterrupt (Ctrl-C)
    try:
        while(True):
			time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    logger.stop()


if __name__ == '__main__':
    main()
