# PyU4V
A library showing some of the functionality possible using the ReST API of Dell EMC's UniSphere for VMAX.
This code has been adapted from https://github.com/scottbri/PyVMAX.
Get the Unisphere for VMAX Rest documentation by navigating to https://<ip-address>:<port-number>/univmax/restapi/docs,
where <ip-address> = the ip of your Unisphere server and <port-number> = the corresponding port to connect through,
eg: https://10.0.0.1:8443/univmax/restapi/docs.

# WHAT'S SUPPORTED
This package supports Unisphere version 8.3 onwards, although the calls *should* work on 8.0, 8.1 and 8.2 also.
We support VMAX3 and VMAX All-Flash (All Flash from 8.3 onwards).

# INSTALLATION
To give it a try, install the package using pip (pip install PyU4V). Copy the sample PyU4V.conf into your working
directory, and add your server and array details to the top of the PyU4V.conf configuration file, under the [setup]
heading. Alternatively, you can pass some or all of these details on initialisation.
Password, username, server_ip, port, and array MUST be set (either in the config file or on initialisation).
Verify can be left as is, or you can enable SSL verification by following the directions below
(see SSL CONFIGURATION).

# SSL CONFIGURATION
1. Get the CA certificate of the Unisphere server.
	$ openssl s_client -showcerts -connect {server_hostname}:8443 </dev/null 2>/dev/null|openssl x509 -outform PEM > {server_hostname}.lss.emc.com.pem
    (This pulls the CA cert file and saves it as server_hostname.lss.emc.com.pem e.g. esxi01vm01.lss.emc.com.pem)
2.	Copy the pem file to the system certificate directory
	$ sudo cp {server_hostname}.lss.emc.com.pem /usr/share/ca-certificates/{server_hostname}.lss.emc.com.lss.emc.com.crt
3. 	Update CA certificate database with the following commands
	$ sudo dpkg-reconfigure ca-certificates (Ensure the new cert file is highlighted)
	$ sudo update-ca-certificates
4. In the conf file insert the following:
   verify=/path-to-file/irco3sd23vm08.lss.emc.com.pem OR pass the value in on initialization.

# USAGE
PyU4V could also be used as the backend for a script, or a menu etc. Just import the PyU4V package (import PyU4V),
create an instance of rest_functions (e.g. "rf = PyU4V.rest_functions()"), and you're good to go.

If you wish to query another array without changing the configuration file, call the set_array() function.

# EXAMPLES
There are a number of examples which can be run with minimal set-up. For details on how to run these,
and other very useful information, please see Paul Martin's blog https://community.emc.com/people/PaulCork/blog

# FUTURE
This is still a work in progress. To be expected in the future:
- Expansion of the rest_functions library (including new Unisphere versions - see below)
- Increased exception handling and logging
- Unittests

# VERSION FUTURE
The Rest API is undergoing substantial transformation for the 8.4 release. With that in mind, we will be creating a
new 84 version when that is released.

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
