#!/usr/bin/python
import os
import time

def devlist(config):
    '''
    scan devices in /sys/block according to config file
    if config is none, every device is scanned

    return list of found devices or emty list
    '''
    return map(lambda x: '/sys/block/' + x, os.listdir('/sys/block')) #TODO Config goes here...

def get_stat(dev):
    '''
    return new stat values (absolute numbers) for specified device
    return values as dictionary or None if error occure

    format from linux Documentation/block/stat.txt:

    Name            units         description
    ----            -----         -----------
    read I/Os       requests      number of read I/Os processed
    read merges     requests      number of read I/Os merged with in-queue I/O
    read sectors    sectors       number of sectors read
    read ticks      milliseconds  total wait time for read requests
    write I/Os      requests      number of write I/Os processed
    write merges    requests      number of write I/Os merged with in-queue I/O
    write sectors   sectors       number of sectors written
    write ticks     milliseconds  total wait time for write requests
    in_flight       requests      number of I/Os currently in flight
    io_ticks        milliseconds  total time this block device has been active
    time_in_queue   milliseconds  total wait time for all requests

    return value is just dictionary of those values (11 items)
    '''
    retval={}
    f=open(dev+'/stat','r')
    split=f.readline().split()
    retval["read_ios"]      = int(split[0])
    retval["read_merges"]   = int(split[1])
    retval["read_sectors"]  = int(split[2])  #TODO add getdevsize for right IO in MB/s calculation
    retval["read_ticks"]    = int(split[3])  #TODO get tick length somewhere
    retval["write_ios"]     = int(split[4])
    retval["write_merges"]  = int(split[5])
    retval["write_sectors"] = int(split[6])
    retval["write_ticks"]   = int(split[7])
    retval["in_flight"]     = int(split[8])
    retval["io_ticks"]      = int(split[9])
    retval["time_in_queue"] = int(split[10])


    return retval

def calc_single_delta(new,old):
    '''
    return 'delta' values between old and new
    format is same as get_stat, but contains delta, not absolute values
    (N.B. delta is absolute and does not divided for dt)
    '''
    retval={}
    for key in old.iterkeys():
        retval[key]=new[key]-old[key]
    return retval

def calc_delta(old, new):
    '''
       return dict of deltas for two dict of dicts
    '''
    retval={}
    for key in old.iterkeys():
        if key == '/sys/block/sda':
		print "debug", "-"*40+'\n',new[key],'-'*40+'\n', old[key], '='*50+'\n'
        retval[key]=calc_single_delta(new[key],old[key])
    return retval

def scan_all(devlist):
    '''
        performs full scan for all devices in devlist
        return dict in format:
          key=devname
          values=dict of stat
    '''
    retval={}
    for dev in devlist:
        retval[dev]=get_stat(dev)
    return retval

def tick(devlist, delay):
    '''
        yield new values
    '''
    old=scan_all(devlist)
    while 1:
        time.sleep(delay)
        new=scan_all(devlist)
        yield calc_delta (old,new)

def view(delta):
    '''
        Visualisation part: print (un)fancy list
    '''
    #print delta['/sys/block/sda']
    return None

def main():
    '''
    Right now we don't accept any command line values and 
    don't use config file (initial proof of usability)
    We making 1s tick so we can use delta as ds/dt
    '''
    config=None
    for a in tick(devlist(config),5):
	view (a)

if __name__ == '__main__':
    main ()

