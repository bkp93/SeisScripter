This program uploads a bash script and runs it on groups of remote devices, for example on
every TitanSMA in the PNSN network. Results are stored in a csv, where the first
column is the site code and the second column contains the output of your script.

In order to run program, you must first create a "params.py" file and a "private.py" file.
Included in the distribution is an example params template that can be used to get started.

The TESTING variable tells the program to run on a manually specified set of sites. These should
be specified in a file called "site_ip_port.csv" and the format should be:

Site Code,IP,Port

SITE,XXX.XXX.XXX.XXX,22

It cannot contain null values.

Other required files to run:
params.py
private.py
input/testing_ips.csv    (Only required if TESTING is true)

I have included templates of the params.py and private.py, but they should be customized for you.
