from libs.theloop import TheLoop
from multiprocessing import Process, Pipe
import logging

logger = logging.getLogger('mats')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(levelname)s %(asctime)s %(message)s'))
logger.addHandler(ch)

theloop = TheLoop()
theloop.loop()

