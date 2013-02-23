import ConfigParser, sys, traceback, logging

logConfig = ConfigParser.RawConfigParser()
logConfig.read('scripts.cfg')

# Logger File Handler
logLFH = logging.FileHandler(logConfig.get('LogUncaught', 'log_location'))
logLFH.setLevel(logging.DEBUG)

# Logger Console Handler
logLCH = logging.StreamHandler()
logLCH.setLevel(logging.ERROR)

# Logger Formatter
logLFH.setFormatter(logging.Formatter('[%(asctime)s | %(levelname)s]  - %(message)s'))
logLCH.setFormatter(logging.Formatter(' %(message)s'))

# Logger
logLogger = logging.getLogger("loguncaught_logger")
logLogger.setLevel(logging.DEBUG)
logLogger.addHandler(logLFH)
logLogger.addHandler(logLCH) 

def logException(type, value, tb):
   messageType = '{0}: {1}'.format(type, value)
   messageTraceback = ''.join(traceback.format_tb(tb))
   logLogger.critical(messageType)
   logLogger.critical(messageTraceback)

sys.excepthook = logException