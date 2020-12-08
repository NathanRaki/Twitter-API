#%% Importing Libraries
import os
import json
os.chdir('/home/raki/Repositories/twitter/')
from FarFarAway import FarFarAway

#%%
ffa = FarFarAway()

#ffa.loadfriends()

# Follow x users, splitted in different filters
ffa.autofollow(100)

#%%

with open("followed.json") as json_file:
    followed = json.load(json_file)
    
print(len(followed))