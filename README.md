# PyU4V
A library showing some of the functionality possible using the ReST API of EMC's UniSphere for VMAX.
A lot of the heavy lifting was done for me; this code has been adapted from https://github.com/scottbri/PyVMAX

To give it a try, download the files and add your server and array details to the top of the PyU4V.conf
configuration file, under the [setup] heading.
Password, username, server_ip, port, and array MUST be set. Cert and verify can be left as is.

Then use the example.py file as, well, an example, and start calling functions!

The rest_univmax file could also be used as the backend for a script, or a menu etc.

If you wish to query another array without changing the configuration file, call the set_array() function.

This is still a work in progress, I'll be working on it (and corresponding documentation!) whenever I get the chance!