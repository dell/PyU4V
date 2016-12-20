# PyU4V
A library showing some of the functionality possible using the ReST API of Dell EMC's UniSphere for VMAX.
A lot of the heavy lifting was done for me; this code has been adapted from https://github.com/scottbri/PyVMAX.
Also see the Dell EMC Rest documentation by navigating to URL/univmax/restapi/docs
eg: https://10.0.0.1:8443/univmax/restapi/docs.

# INSTALLATION
To give it a try, download the files and add your server and array details to the top of the PyU4V.conf
configuration file, under the [setup] heading.
Requires the 'requests' library (can be installed using pip).
Password, username, server_ip, port, and array MUST be set. Cert and verify can be left as is.

# USAGE
example.py can be run directly, just make sure to assign the variables. PyU4V could also be used as the backend
for a script, or a menu etc. Just move the PyU4V package into your working directory and import like so
'from PyU4V.rest_univmax import rest_functions' and you're good to go. Be sure to bring the configuration file with you.

If you wish to query another array without changing the configuration file, call the set_array() function.

# FUTURE
This is still a work in progress, and it's far from polished.
I'll be working on it (and corresponding documentation!) whenever I get the chance!
I will keep expanding the rest_functions library, and also try and keep on top of any code changes in the ReST API
itself.

# CONTRIBUTION
Please do! Create a fork of the project into your own reposity. Make all your necessary changes and create a pull
request with a description on what was added or removed and details explaining the changes in lines of code.
If it all looks good, I'll merge it.

# SUPPORT
Please file bugs and issues on the Github issues page for this project. This is to help keep track and document
everything related to this repo. For general discussions and further support you can join the {code} Community
slack channel. Lastly, for questions asked on Stackoverflow.com please tag them with EMC. The code and
documentation are released with no warranties or SLAs and are intended to be supported through a community driven
process.