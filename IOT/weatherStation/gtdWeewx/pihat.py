import Adafruit_BMP.BMP280 as BMP280
import Adafruit_DHT
import weewx.drivers
import time

DRIVER_NAME = 'PiHat'
DRIVER_VERSION = '0.1'

def loader(config_dict, engine):
    return PiHatDriver(**config_dict[DRIVER_NAME])

class PiHatDriver(weewx.drivers.AbstractDevice):
    def __init__(self, **stn_dict):
        self._sensor1 = BMP280.BMP280()
        self._sensor2 = Adafruit_DHT.AM2302
        self._pin = 17

    def genLoopPackets(self):
        while True:
            try:
                packet = dict()
                packet['dateTime'] = int(time.time() + 0.5)
                #packet['usUnits'] = weewx.US
                packet['usUnits'] = weewx.METRIC
                #packet['usUnits'] = weewx.METRICX
                #packet['inTemp'] = self._sensor1.read_temperature()*9/5+32
                #packet['pressure'] = self._sensor1.read_pressure()*0.00029529980164712
                packet['inTemp'] = self._sensor1.read_temperature()
                packet['pressure'] = self._sensor1.read_pressure()/100
                packet['outHumidity'], packet['outTemp'] = Adafruit_DHT.read_retry(self._sensor2, self._pin)
                yield packet
            except IOError, e:
                syslog.syslog(syslog.LOG_ERR, "get data failed: %s" % e)
