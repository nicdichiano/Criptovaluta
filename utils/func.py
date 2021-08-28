import os
import yaml

with open('./config.yaml') as f:
    config=yaml.safe_load(f)

def get_keys(owner):
    with open(os.path.join(config['path_credentials'],'keys_'+owner),'r') as file:
        for line in file:
           if 'private_key' in line:
               private_key=line.split(':')[-1].strip()   #divide in due parti la riga e prende solo la seconda parte (l'esadecimale) eliminando gli spazi (strip)
           elif 'public_key' in line:
               public_key=line.split(':')[-1].strip()
    return private_key,public_key
