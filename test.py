from blockchain import *
from proof_stake import *

with open('./config.yaml') as f:
    config=yaml.safe_load(f)
try:
    chain=pickle.load(open(os.path.join(config['path_chain'],config['name_chain']),'rb'))
    cyber_chain=BlockChain(chain)
    cyber_chain.is_chain_valid()
    print('Blockchain caricata correttamente') 
except:
    cyber_chain=BlockChain()
    cyber_chain.is_chain_valid()
    print('Blockchain creata')

private_key_marco,public_key_marco=get_keys('marco')
private_key_mario,public_key_mario=get_keys('mario')
private_key_sara,public_key_sara=get_keys('sara')
private_key_polo,public_key_polo=get_keys('polo')
private_key_root,public_key_root=get_keys('root')

dp1=Transaction(public_key_root,public_key_marco,100)
dp1.sign_transaction(private_key_root)
cyber_chain.add_transactions(dp1)


# dp2=Transaction(public_key_root,public_key_marco,100)
# dp2.sign_transaction(private_key_root)
# cyber_chain.add_transactions(dp2)
# cyber_chain.mining_pending_transactions(public_key_mario)
# cyber_chain.content()
# cyber_chain.is_chain_valid()

# dp2=Transaction(public_key_root,public_key_mario,300)
# dp2.sign_transaction(private_key_root)
# cyber_chain.add_transactions(dp2)
# cyber_chain.mining_pending_transactions(public_key_mario)
# cyber_chain.content()
# cyber_chain.is_chain_valid()

dp2=Transaction(public_key_root,public_key_sara,1000)
dp2.sign_transaction(private_key_root)
cyber_chain.add_transactions(dp2)
#cyber_chain.mining_pending_transactions(public_key_mario)
#cyber_chain.content()
cyber_chain.is_chain_valid()

#proof of stake
proof(cyber_chain)
