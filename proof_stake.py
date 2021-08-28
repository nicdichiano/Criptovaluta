from blockchain import *

def proof(cyber_chain):
    private_key_marco,public_key_marco=get_keys('marco')
    private_key_mario,public_key_mario=get_keys('mario')
    private_key_sara,public_key_sara=get_keys('sara')
    private_key_polo,public_key_polo=get_keys('polo')
    private_key_root,public_key_root=get_keys('root')
    indirizzi=[]
    balances=[]
    with open(os.path.join(config['path_credentials'],'indirizzi'),'r') as file:
        for line in file:
            if 'public_key' in line:
                 indirizzi.append(line.split(':')[-1].strip())
    for ind in indirizzi:
        balances.append(cyber_chain.get_balance(ind))
        balance_max=max(balances)
    indice=balances.index(balance_max)

    cyber_chain.mining_pending_transactions(indirizzi[indice])                                      
    cyber_chain.content()
#cyber_chain.chain[1].transactions[0].amount=200
    cyber_chain.is_chain_valid()
    print(cyber_chain.get_balance(public_key_sara))
    print(cyber_chain.get_balance(public_key_root))


