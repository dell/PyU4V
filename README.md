# PyU4V
A library showing some of the functionality possible using the ReST API of Dell EMC's UniSphere for VMAX.
This code has been adapted from https://github.com/scottbri/PyVMAX.
Get the Unisphere for VMAX Rest documentation by navigating to https://<ip-address>:<port-number>/univmax/restapi/docs,
where <ip-address> = the ip of your Unisphere server and <port-number> = the corresponding port to connect through,
eg: https://10.0.0.1:8443/univmax/restapi/docs.

# VERSION 3
Please note that version 3 of the library is NOT BACKWARDS COMPATIBLE with existing scripts, and does not support any
Unisphere for VMAX version earlier that 8.4 - PyU4V version 2.0.2.5 is still available on Pip and a tagged repoisitory
is available on Github. Version 3 will be the version maintained going forward, and we do suggest you move to this
version when possible.

# WHAT'S SUPPORTED
This package supports Unisphere version 8.4 onwards. We support VMAX3 and VMAX All-Flash.

# INSTALLATION
To give it a try, install the package using pip (pip install PyU4V). Copy the sample PyU4V.conf into your working
directory, and add your server and array details to the top of the PyU4V.conf configuration file, under the [setup]
heading. Alternatively, you can pass some or all of these details on initialisation.
Password, username, server_ip, port, and array MUST be set (either in the config file or on initialisation).
Verify can be left as is, or you can enable SSL verification by following the directions below
(see SSL CONFIGURATION).

# SSL CONFIGURATION
1. Get the CA certificate of the Unisphere server.
	$ openssl s_client -showcerts -connect {server_hostname}:8443 </dev/null 2>/dev/null|openssl x509 -outform PEM > {server_hostname}.pem
    (This pulls the CA cert file and saves it as server_hostname.pem e.g. esxi01vm01.pem)
2.	Either (a) add the certificate to a ca-certificates bundle, OR (b) add the path to the conf file:
    a.
        - Copy the pem file to the system certificate directory:
	      $ sudo cp {server_hostname}.pem /usr/share/ca-certificates/{server_hostname}.crt
        - Update CA certificate database with the following commands
	      $ sudo dpkg-reconfigure ca-certificates (Ensure the new cert file is highlighted)
	      $ sudo update-ca-certificates
	    - In the conf file ensure "verify=True" OR pass the value in on initialization
	b.
        In the conf file insert the following:
        verify=/{path-to-file}/{server_hostname}.pem OR pass the value in on initialization.

# USAGE
PyU4V could also be used as the backend for a script, or a menu etc.
Just import the PyU4V package (import PyU4V), create an instance of RestFunctions "rf = PyU4V.RestFunctions()",
and you're good to go. The functions are divided up into categories - common, provisioning, replication and performance,
e.g. "rf.provisioning.get_host_list()"; "rf.replication.find_expired_snapvx_snapshots()"

If you wish to query another array without changing the configuration file, call the 'set_array_id(new_array_id)'
function, e.g. 'rf.set_array_id('000197123456')'.

# EXAMPLES
There are a number of examples which can be run with minimal set-up. For details on how to run these,
and other very useful information, please see Paul Martin's blog https://community.emc.com/people/PaulCork/blog

# FUTURE
This is still a work in progress. To be expected in the future:
- Expansion of the rest_functions library
- Increased exception handling and logging
- Unittests

# CONTRIBUTION
Please do! Create a fork of the project into your own repository. Make all your necessary changes and create a pull
request with a description on what was added or removed and details explaining the changes in lines of code.
If it all looks good, I'll merge it.

# SUPPORT
Please file bugs and issues on the Github issues page for this project. This is to help keep track and document
everything related to this repo. For general discussions and further support you can join the {code} Community
slack channel. Lastly, for questions asked on Stackoverflow.com please tag them with EMC. The code and
documentation are released with no warranties or SLAs and are intended to be supported through a community driven
process.
