import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn()

# Create a Clone Copy of a Stoage group, The Target Storage Group will be
# created with all required volumes for the clone copy if it does not exist
# already.
conn.clone.restore_clone(
    storage_group_id="clonesrc", target_storage_group_id="clonetgt")

# Splits the Restore Session to Remove the Restored Flag from Clone Session.

conn.clone.split_clone(
    storage_group_id="clonesrc", target_storage_group_id="clonetgt")

# Close the session
conn.close_session()
