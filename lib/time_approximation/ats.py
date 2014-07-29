from datetime import datetime
from urllib.error import HTTPError
import urllib.request

__author__ = 'sighalt'


class ATSRequest(object):
    """
    Represents a webrequest which is measured in some ways interesting for Adversarial Time Synchronisation.

    Measurement values are taking place when `fire()` is called at least once.
    """

    def __init__(self, url):
        """
        Constructor

        @type url: str
        @param url: the URL of the request
        """
        self.url = url
        self.start_time = None
        self.end_time = None
        self.response = None

    def fire(self):
        """
        Send the request.

        Set `self.start_time` and `self.end_time` as UTC datetime objects.
        In case of an HTTP error, the error object is returned.

        @rtype: ATSRequest
        @return: the request object
        """
        self.start_time = datetime.utcnow()
        try:
            self.response = urllib.request.urlopen(self.url)
        except HTTPError as e:
            self.response = e
        self.end_time = datetime.utcnow()

        return self

    @property
    def remote_time(self):
        """
        The HTTP header field 'Date' as datetime object.

        @rtype: datetime
        @return: the HTTP header field 'Date'
        """
        if self.response is None:
            raise AttributeError("Time was not measured yet.")
        try:
            time_str = self.response.headers['Date']
        except KeyError:
            return None

        dt = datetime.strptime(time_str, "%a, %d %b %Y %H:%M:%S %Z")

        return dt

    @property
    def local_time_consumption(self):
        """
        The complete time consumption of this request.

        @rtype: timedelta
        @return: the timedelta between start and end of sending and receiving this request.
        """
        if self.start_time is None or self.end_time is None:
            raise AttributeError("Time consumption was not measured yet.")

        return self.end_time - self.start_time


class ATSRequestPair(object):
    """
    Since Adversarial Time Synchronisation Requests are normally sent as a pair of two, this class represent such a
    pair.
    """

    def __init__(self, url):
        """
        Constructor

        @type url: str
        @param url: the url of the requests
        """
        self.r1 = ATSRequest(url)
        self.r2 = ATSRequest(url)

    def send(self):
        """
        Send the two requests.
        """
        self.r1.fire()
        self.r2.fire()

    def is_useful(self):
        """
        In ATS request pairs are needed whose requests differ in the 'Date' header between one second.

        If the delta is more than a second the epoch is too large to get reliable round trip times.
        If the delta is not a second, the request pair is unusable in context of ATS because of no difference.

        @rtype: bool
        @return: weather the 'Date' header fields of this request pair differ in one second
        """
        delta = self.r2.remote_time - self.r1.remote_time

        # if delta > 1: too long epoch to determine S
        # if delta < 1: event S not happened
        return int(delta.total_seconds()) == 1

    @property
    def avg_rtt(self):
        """
        The average round trip time of this request pair.

        @rtype: float
        @return: the average round trip time in seconds
        """
        sum_time_consumption = self.r1.local_time_consumption + self.r2.local_time_consumption

        return sum_time_consumption.total_seconds() / 2


class AdversarialTimeSynchronization(object):
    """
    Implements the Adversarial Time Synchronization with a remote webserver.
    """

    def __init__(self, url):
        """
        Constructor.

        @type url: str
        @param url: the url used for time synchronisation
        """
        self.url = url
        self.rtts = []

    def collect_data(self, n=10):
        """
        Collect usable data sets up to a number of `n`.

        If data was already collected, `n` new data sets will be appended.

        @type n: int
        @param n: the number of data sets to collect
        """

        while n > 0:
            pair = ATSRequestPair(self.url)

            pair.send()

            if pair.is_useful():
                print("[+] Useful pair found")
                self.rtts.append(pair.avg_rtt)
                n -= 1

    @property
    def approximated_delta(self):
        """
        The approximated time delta between the send date of the collected request and the zeroing of the microseconds.

        This value can be used to approximate the execution time of a e.g. uniqid() call.

        @rtype: float
        @return: approximated time delta
        """
        deltas = [rtt/2 for rtt in self.rtts]

        return sum(deltas) / len(deltas)
