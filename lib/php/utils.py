__author__ = 'sighalt'


def uniqid2time(uniqid, more_entropy=False):
    """
    Return a tuple holding the unix time and number of microseconds provided by the return of php's "uniqid" function.

    Background:

        The return of php's uniqid function is a concatenated string consists of the hex converted unixtime and the
        hex converted number of microseconds.

    @type uniqid: str
    @param uniqid: the output of php's function "uniqid"
    @type more_entropy:  bool
    @param more_entropy: weather the more_entropy flag was set
    @rtype: tuple
    @return: a tuple in the format (unix_time, microseconds)
    """
    unix_time = uniqid[:8]
    microsecs = uniqid[-5:]

    return int(unix_time, 16), int(microsecs, 16)


def time2uniqid(unix_time, microsecs):
    """
    Generate a unique string as provided by php's uniqid function based on `unixtime` and `microsecs`.

    @type unix_time: int
    @param unix_time: unix time
    @type microsecs: int
    @param microsecs: microsecond part of the provided unix time
    @rtype: str
    @return: a unique string as provided by php's uniqid function
    """
    # when not 'zfill'-ing there might be missing a zero in the uniqid
    return hex(unix_time)[2:].zfill(8) + hex(microsecs)[2:].zfill(5)
