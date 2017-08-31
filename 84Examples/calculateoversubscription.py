#Quick Script to calculate oversubscription for a given array.

from PyU4V import RestFunctions
ru = RestFunctions(u4v_version='84')
ru.array_id="12 Digit Serial Number"
srp_details, rc = ru.get_srp("SRP_1")


print (srp_details)

total_subscribed_cap_gb = srp_details.get ('total_subscribed_cap_gb')
total_usable_cap_gb = srp_details.get ('total_usable_cap_gb')

print ("OverSubscription is %s"  %
       (total_subscribed_cap_gb/total_usable_cap_gb))

