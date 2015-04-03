import logging
import socket
import datetime
import time

from sniffeq.settings import GRAPHITE_CARBON_HOST, GRAPHITE_CARBON_PORT
from sniffeq.models.presentation import Presentation


log = logging.getLogger('handlers.statshandler')

class SEStatsHandler(object):
    """
    Sends data into graphite
    """

    def populate(self):
        """
        Populate DB
        """
        metric_form = 'sniffeq.test.{companyName}.{form}.{metricName}'
        timestamp_map = {
            'Q1': time.mktime(datetime.datetime(2014, 3, 1, 0, 0, 0).timetuple()),
            'Q2': time.mktime(datetime.datetime(2014, 6, 1, 0, 0, 0).timetuple()),
            'Q3': time.mktime(datetime.datetime(2014, 9, 1, 0, 0, 0).timetuple()),
            'Q4': time.mktime(datetime.datetime(2015, 1, 1, 0, 0, 0).timetuple()),
        }
        for presentation in Presentation.objects.filter(stmt='IS'):
            submission = presentation.submissionRef

            if not submission:
                continue

            timestamp = timestamp_map.get(submission.fp)
            metric = metric_form.format(
                companyName=submission.name.lower().replace(' ', '_').replace('-', '_'),
                form=submission.form.replace('-', '_'),
                metricName=presentation.tag,
            )

            value = 0
            for item in presentation.numbersRef:
                value = item.value or 0
                value += value

            if timestamp:
                self.send(metric, value, int(timestamp))
                #self.send('github.visits.count', random.randrange(0, 10000), int(timestamp))

    def send(self, metric, message, timestamp):
        """
        Handles sending data to graphite
        """
        message = '%s %s %s\n' % (metric, message, timestamp)
        log.info('Sending message: %s', message)
        sock = socket.socket()
        sock.connect((GRAPHITE_CARBON_HOST, GRAPHITE_CARBON_PORT))
        sock.sendall(message)
        sock.close()
        log.info('Message sent!')


if __name__ == '__main__':
    stats = SEStatsHandler()
    stats.populate()
