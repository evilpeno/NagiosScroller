#!/usr/bin/env python
#
# nagios_text_summary.py - This program produces a plain-text summary
# similar to that found on the Service Detail page of nagios.
#
# I use this script to generate daily email reports from a cron job.
#
# Usage: Install into your nagios cgi-bin directory.  To create
# the report point wget, curl, or your webbrowser to 
# http://your.nagios.server/cgi-bin/nagios_text_summary.py
#
import os, time

# Map the host and service enumerations to readable text
HOST_STATE_MAP = {"0": "UP", "1": "DOWN"}
STATE_MAP = {"0": "OK", "1": "WARNING", "2": "CRITICAL", "3": "UNKNOWN"}

def parse_objects_file(filepath):
   """Parse a nagios objects.dat file.  Returns
   a list of dictionaries, one dictionary per object."""
   OBJECTS=open(filepath)
   objects = []
   while 1:
       line = OBJECTS.readline()
       if not line:
           break

       line = line.strip()
       if line.startswith("#"):
           # A Comment
           pass

       elif line.startswith("define") and line.find('{') != -1:
           type = line[0:line.find('{')].strip().split(" ")[1]
           object = {}

           # Now read all the details
           while 1:
               line = OBJECTS.readline()
               line = line.strip()
               if not line:
                   break
               elif line.find("\t") != -1:
                   name, value = line.split("\t", 1)
                   name = name.strip()
                   value = value.strip()
                   object[name] = value
               elif line.find("}") != -1:
                   objects.append((type, object))
                   break
   return objects

def parse_status_file(filepath):
   """Parse a nagio status.dat file.  Returns a
   dictionary where the primary keys are the hostnames.  For each
   host all of the services are listed in the 'services' key; the other
   key elements are used for host details."""
   STATUS=open(filepath)
   summary = {}
   while 1:
       line = STATUS.readline()
       if not line:
           break

       line = line.strip()
       if line.startswith("#"):
           # A Comment
           pass

       elif line.find('{') != -1:
           statustype = line[0:line.find('{')]
           if statustype.strip() == "hoststatus":
               # We except host_name and service_description first
               line = STATUS.readline()
               name, hostname = line.split("=", 1)
               name = name.strip()
               hostname = hostname.strip()
               if name != "host_name":
                   continue
               if not summary.has_key(hostname):
                   summary[hostname] = {}
                   summary[hostname]['services'] = {}
               # Now read all the details
               while 1:
                   line = STATUS.readline()
                   if not line:
                       break
                   elif line.find("=") != -1:
                       name, value = line.split("=", 1)
                       name = name.strip()
                       value = value.strip()
                       summary[hostname][name] = value
                   elif line.find("}") != -1:
                       break

           elif statustype.strip() == "servicestatus":
               # We except host_name and service_description first
               line = STATUS.readline()
               name, hostname = line.split("=", 1)
               name = name.strip()
               hostname = hostname.strip()

               line = STATUS.readline()
               name, service_desc = line.split("=", 1)
               name = name.strip()
               service_desc = service_desc.strip()
               if name != "service_description":
                   continue
               summary[hostname]['services'][service_desc] = {}
               # Now read all the details
               while 1:
                   line = STATUS.readline()
                   if not line:
                       break
                   elif line.find("=") != -1:
                       name, value = line.split("=", 1)
                       name = name.strip()
                       value = value.strip()
                       summary[hostname]['services'][service_desc][name] = value
                   elif line.find("}") != -1:
                       break
   return summary

def pretty_print_status():
   """Produce a pretty printed textual representation of the nagios service
   detail summary."""
   # This program assumes it is installed in the nagios cgi-bin directory
   objects = parse_objects_file("/var/nagios/objects.cache")
   summary = parse_status_file("/var/nagios/status.dat")

   # Pretty print the status
   #print "%-12s%-25s%-10s%-34s%-20s" % ("Host", "Service", "Status", "Acknowledged", "Last Checked")
   hosts = summary.keys()
   hosts.sort()
   for host in hosts:
       #print "---------------------------------------------------------------------------------------------------------"
       status = summary[host]
       host_state = HOST_STATE_MAP[status['current_state']]
       last_checked = time.asctime(time.localtime(int(status['last_check'])))  # or gmtime if servi is GMT
       ack = ""
       if host_state != "UP" and status['problem_has_been_acknowledged'] == "1":
           ack = "YES"
       elif host_state != "UP" and status['problem_has_been_acknowledged'] == "0":
           ack = "NO"
       # Use pretty print host aliases
       hostalias = host
       for objtype, object in objects:
           if objtype == "host" and object['host_name'] == host:
               try:
                   hostalias = object['alias']
               except KeyError:
                   hostalias = host
       old_host = ""
       current_host=hostalias
       #print "%-39s%-10s%-20s%-12d%-20s" % (hostalias,  host_state, ack, int(status['last_check']), last_checked)
       #print "%s|%s|%s|%-12d" % (hostalias,  host_state, ack, int(status['last_check']))
       services = summary[host]['services'].keys()
       services.sort()
       for service in services:
           status = summary[host]['services'][service]
           current_state = STATE_MAP[status['current_state']]
           last_checked = time.asctime(time.localtime(int(status['last_check']))) # or gmtime if servi is GMT
           ack = ""
           if host_state == 'DOWN':
               # Don't report service status because it would be inaccurate
               current_state = ""
               ack = ""
           else:
               # Only print the ack state if the servie/host actually has a problem
               if current_state != "OK" and ( status['problem_has_been_acknowledged'] == "1" or status['notifications_enabled'] == "0" ):
                   ack = "YES"
               elif current_state != "OK" and status['problem_has_been_acknowledged'] == "0":
                   ack = "NO"
           if current_state != "OK":
               if current_host != old_host:
                   print "%-39s%-10s%-20s%-12d" % (hostalias,  host_state, ack, int(status['last_check']))
                   old_host = current_host
               print "%-14s%-25s%-10s%-20s%-12d" % ("", service, current_state, ack, int(status['last_check']))
           #print "%s|%s|%s|%s|%-12d" % ("", service, current_state, ack, int(status['last_check']))
if __name__ == "__main__":
    # Print the HTTP header info
    print "Content-Type: text/plain"
    print

    # Now print the actual data
    try:
        pretty_print_status()
    except Exception, e:
       print "Internal Error -", e


