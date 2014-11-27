from datetime import datetime, timedelta as td
import argparse
import os
import shutil
import subprocess
import sys
import time
import urllib as ul

def check_dir(p):
    if not os.path.exists(p):
        os.makedirs(p)


def elm_search(f,s,e,d,w,l):
    cnt = 0
    st = int(time.mktime(s.timetuple()))
    et = int(time.mktime(e.timetuple()))
    mt = st
    while mt < et :
        st = int(time.mktime((s + td(seconds=d*cnt)).timetuple()))
        mt = int(time.mktime((s + td(seconds=d*(cnt+1))).timetuple()))
        wd = w + str(st) + "_"  + str(mt) + "/"
        check_dir(wd)
        print "/usr/local/bin/elmsearch wd=" + wd + " st=" + str(st) + " et=" + str(mt) + " nr=/%5E%2E%2A%24/e mr=/" + f + "/ mb=1024"
        l.write("/usr/local/bin/elmsearch wd=" + wd + " st=" + str(st) + " et=" + str(mt) + " nr=/%5E%2E%2A%24/e mr=/" + f + "/ mb=1024")
        subprocess.call(["/usr/local/bin/elmsearch", "wd=" + wd, "st=" + str(st), "et=" + str(mt), "nr=/%2E%2E%2A%24/e", "mr=/" + f + "/", "mb=1024" ], stdout=l)
        cnt+=1


if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Raw log extractor for McAfee ESM")
    parser.add_argument("-l", action='store', dest="l", type=str, default="elmlog.txt", help="Path to log file")
    parser.add_argument("-d", action='store', dest="d", type=str, required=True, help="Temporary directory /ss1/usr/local/elm/tmp/")
    parser.add_argument("-st", action='store', dest="st", type=int, required=True, help="Start Time (Unix Timestamp)")
    parser.add_argument("-et", action='store', dest="et", type=int, required=True, help="End Time (Unix Timestamp)")
    parser.add_argument("-mr", action='store', dest="mr", type=str, required=True, help="Pattern (Posix regexp surrounded with double quotes)")
    parser.add_argument("-sd", action='store', dest="sd", type=int, default=0, help="Slice in days (stacks with sh,sm,ss)")
    parser.add_argument("-sh", action='store', dest="sh", type=int, default=0, help="Slice in hours (stacks with sd,sm,ss)")
    parser.add_argument("-sm", action='store', dest="sm", type=int, default=0, help="Slice in minutes (stacks with sd,sh,ss)")
    parser.add_argument("-ss", action='store', dest="ss", type=int, default=0, help="Slice in seconds (stacks with sd,sh,sm)")
    args = parser.parse_args()
	
    st=0
    et=0

    # Check if start date before end date
    if args.st >= args.et :
        print "Start Date must be before End Date"
        exit()

    st=datetime.fromtimestamp(args.st)
    et=datetime.fromtimestamp(args.et)

    # Calculation of delta
    delta=td()
    if 0 <= args.sd <= 31 :
        delta += td(days=args.sd)
    else :
        print "Number of days should be between 1 and 31"
    if 0 <= args.sh <= 23 :
        delta += td(hours=args.sh)
    else :
        print "Number of hours should be between 1 and 23"
    if 0 <= args.sm <= 59 :
        delta += td(minutes=args.sm)
    else :
        print "Number of minutes should be between 1 and 59"
    if 0 <= args.ss <= 59 :
        delta += td(seconds=args.ss)
    else :
        print "Number of seconds should be between 1 and 59"

    if delta == 0:
        print "WARNING : No slice defined !! Final result could be truncated"
    
    de=int(delta.total_seconds())
    
    # Working directory
    wd = "/ss1/usr/local/elm/tmp/" + args.d + "/"
    
	# Check if directory exists
    if not os.path.exists(wd):
        # Create directory
        os.makedirs(wd)
    else:
        # Ask if the directory should be deleted
        print "Directory already exists, maybe you would like to empty it ?"
        c = ''
        while c not in ['Y','y','N','n']:
            # Catch single characters
            c = raw_input('Enter Y / N \n')[:1]
        if c in ['y','Y']:
            # Remove directory recursively
            shutil.rmtree(wd)
        else:
            # Do not remove the directory
            print "Directory will not be removed but content can be overwritten"
    
    # Encode the regexp
    f_regex = ul.quote(args.mr)
	
	# Open logfile descriptor
    lf = open(args.l,"w")
	
    elm_search(f_regex, st, et, de, wd, lf)
    
    lf.close()
    
    print "\n"
    print "\n"
    print "Please review the log file (" + args.l + ") to see if your results where truncated or not..." 
    print "\n"
    print "\n"
    print "To merge results :"
    print "\n"
    print "Change directory to " + wd
    print "\n"
    print "Run the following command : find . -name \"result.txt\" | sort | xargs cat > results.txt"
    print "\n"
    print "Don't forget to cleanup your mess when you are finished !!!!"
    print "\n"