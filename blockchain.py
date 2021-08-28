from hashlib import sha256
import json
import yaml
import os
from ecdsa import SigningKey,VerifyingKey,SECP256k1
from datetime import datetime
import pickle
from utils.func import *

class Block:
    def __init__(self,timestamp,transactions,previous_hash=''):
        self.timestamp=timestamp
        self.transactions=transactions    #ci sono più transazioni in un blocco
        self.count=0
        self.previous_hash=previous_hash
        self.hash=self.calculate_hash()
        
        
    def calculate_hash(self):
        if self.previous_hash!="0":   
            temp_transactions=[trans.__dict__ for trans in self.transactions] #prende le transazioni in formato chiave valore
        else:
            temp_transactions=self.transactions
        hash_str=self.timestamp+json.dumps(temp_transactions)+self.previous_hash+str(self.count)   #trasformo e concateno in stringa transazioni e gli altri attributi
        return sha256(hash_str.encode('utf-8')).hexdigest()        #codifica hash della stringa e trasformazione in hexdigest
    
    def content(self):
        msg=self.__dict__.copy()   #copia il blocco sotto forma di dizionario (chiave valore)
        msg_transactions=[]
        for trans in msg['transactions']:
            if self.previous_hash!='0':
                msg_transactions.append(trans.__dict__)
        msg['transactions']=msg_transactions
        print(json.dumps(msg,indent=2,default=str))
        print('--------------------------------------------------------------')
    
    def mining_block(self,difficulty):
        while self.hash[0:difficulty] != '0'*difficulty:     #hash per essere valido deve contenere un numero di zeri iniziali pari a difficulty
            self.count +=1
            self.hash=self.calculate_hash()
        #print('block mined')
    
    def has_valid_transactions(self):
        for trans in self.__dict__['transactions']:
            if trans.is_valid()==False:
                return False
        return True
        
class BlockChain:
    def __init__(self,chain=False):
        self.reward=100
        self.difficulty=3
        if chain:
            self.chain=chain
            self.pending_transactions=[]
        else:
            self.chain=[self.generate_genesis_block()]
            private_key_root,public_key_root=get_keys('root')
            tx_init=Transaction(None,public_key_root,21000000)
            self.pending_transactions=[tx_init]    #Transazione iniziale che conia tutti i token che circoleranno
            self.mining_pending_transactions(public_key_root)
        
        
    def generate_genesis_block(self):
        return Block('24/08/2021','Genesis Block',"0")  #per comodità poniamo il previous address del genesis block pari a 0
    
    #def add_block(self,new_block):
        #new_block.previous_hash=self.chain[-1].hash
        #new_block.hash=new_block.calculate_hash()
        #new_block.mining_block(self.difficulty)    si sostituisce con mining_pending_transactions in quanto per minare il blocco
        #è necessario che tutte le transazioni siano valide
        #inoltre chi ha minato il blocco riceverà una reward
        #self.chain.append(new_block)
    
    def mining_pending_transactions(self,mining_reward_address):
        block=Block(datetime.now().strftime("%d/%m/%y"),self.pending_transactions)
        private_key_root,public_key_root=get_keys('root')
        tx_reward=Transaction(public_key_root,mining_reward_address,self.reward)
        tx_reward.sign_transaction(private_key_root)
        self.pending_transactions.append(tx_reward)
        block.previous_hash=self.chain[-1].hash
        block.mining_block(self.difficulty)
        print('block mined')
        self.chain.append(block)
        self.pending_transactions=[]
    
    def add_transactions(self,transaction):
        if VerifyingKey.from_string(bytearray.fromhex(transaction.from_address),curve=SECP256k1) is None or VerifyingKey.from_string(bytearray.fromhex(transaction.to_address),curve=SECP256k1) is None:
            raise ValueError('from address or to address not valid') 
        if transaction.is_valid()==False:
            raise ValueError('transaction not valid')
        self.pending_transactions.append(transaction)
    
    def get_balance(self,address):
        balance=0
        for block in self.chain[1:]:
            for trans in block.transactions:
                trans=trans.__dict__
                if address==trans['from_address']:
                    balance-=trans['amount']
                elif address==trans['to_address']:
                    balance+=trans['amount']
        return balance
        
        
    def is_chain_valid(self):
        for i in range(1,len(self.chain)):
            if i==0:
                current_block=self.chain[i]
                if current_block.hash!='0':
                    raise ValueError('hash del genesis block non è 0!!')
            else:
                current_block=self.chain[i]
                previous_block=self.chain[i-1]
                if current_block.has_valid_transactions()==False:
                    self.chain=pickle.load(open(os.path.join(config['path_chain'],config['name_chain']),'rb'))
                    raise ValueError('Una o più transazioni  del blocco {current_block[0:8]} non sono valide')
                if current_block.hash!=current_block.calculate_hash():
                    self.chain=pickle.load(open(os.path.join(config['path_chain'],config['name_chain']),'rb'))
                    raise ValueError(f"Chain non valida")
                if current_block.previous_hash!=previous_block.hash:
                    self.chain=pickle.load(open(os.path.join(config['path_chain'],config['name_chain']),'rb'))
                    raise ValueError(f"Chain non valida")
        pickle.dump(self.chain,open(os.path.join(config['path_chain'],config['name_chain']),'wb'))   #conservo la blockchain quando è valida così se viene invalidata è possibile recuperare una copia valida precedente
        print("Chain is valid")
    
    def content(self):
        for block in self.chain:           #stampa contenuto del blocco
            block.content()
                
class Transaction:
    def __init__(self,from_address,to_address,amount):
        self.from_address=from_address
        self.to_address=to_address
        self.amount=amount
        
    def calculate_hash(self):
        hash_str=self.from_address+self.to_address+str(self.amount)
        return sha256(hash_str.encode('utf-8')).hexdigest()
        
        
    def sign_transaction(self,signing_key):
        signing_key=SigningKey.from_string(bytearray.fromhex(signing_key),curve=SECP256k1) #signing_key è la "chiave di firma", alla chiave privata si applica ecdsa
        #controllo che la chiave pubblica sia quella associata a signing_key
        if signing_key.get_verifying_key().to_string().hex() != self.from_address: #puoi firmare solo con la chiave privata associata al from_address
            raise ValueError(f'non sei autorizzato a firmare questa transazione') 
        hash_tr=self.calculate_hash()  #calcolo hash della transazione
        self.signature=signing_key.sign(hash_tr.encode('utf-8')).hex()
        
                                        
    def is_valid(self):
        if self.from_address==None:
            return True
        if self.signature==False or len(self.signature)==0:
            raise ValueError('Missing signature')
        public_key=VerifyingKey.from_string(bytearray.fromhex(self.from_address),curve=SECP256k1)
        try:                               
            public_key.verify(bytes.fromhex(self.signature),self.calculate_hash().encode('utf-8'))
        except Exception as e:
            print(e)
            return False
            
        
# cyber_chain=BlockChain() 

# private_key_marco=SigningKey.generate(SECP256k1)        #generazione chiave privata
# public_key_marco=private_key_marco.get_verifying_key()  #generazione chiave pubblica associata alla chiave privata
# print(private_key_marco)
# print(public_key_marco)
# #trasformazione in stringa esadecimale delle chiavi
# private_key_marco=private_key_marco.to_string().hex()
# print(private_key_marco)
# public_key_marco=public_key_marco.to_string().hex()
# print(public_key_marco)

# #Generazione chiavi per altri due utenti
# private_key_polo=SigningKey.generate(SECP256k1)
# public_key_polo=private_key_polo.get_verifying_key()
# private_key_mario=SigningKey.generate(SECP256k1)
# public_key_mario=private_key_mario.get_verifying_key()


# private_key_polo=private_key_polo.to_string().hex()
# public_key_polo=public_key_polo.to_string().hex()
# private_key_mario=private_key_mario.to_string().hex()
# public_key_mario=public_key_mario.to_string().hex()


# #Esempio di transazioni
# tx1=Transaction(public_key_marco,public_key_polo,100)
# #firma di tx1
# tx1.sign_transaction(private_key_marco)
# cyber_chain.add_transactions(tx1)
# tx2=Transaction(public_key_polo,public_key_marco,30)
# tx2.sign_transaction(private_key_polo)
# cyber_chain.add_transactions(tx2)

# #supponiamo che mario effettua il mining delle transazioni
# cyber_chain.mining_pending_transactions(public_key_mario)


# #istruzione per vedere contenuto dei blocchi
# cyber_chain.content()

# #print(public_key_mario)
# print(cyber_chain.get_balance(public_key_mario))
# print(cyber_chain.get_balance(public_key_marco))
# print(cyber_chain.get_balance(public_key_polo))

# #cyber_chain.chain[1].transactions[0].amount=200
# cyber_chain.is_chain_valid()

# with open('./config.yaml') as f:
#     config=yaml.safe_load(f)
# try:
#     chain=pickle.load(open(os.path.join(config['path_chain'],config['name_chain']),'rb'))
#     cyber_chain=BlockChain(chain)
#     cyber_chain.is_chain_valid()
#     print('Blockchain caricata correttamente') 
# except:
#     cyber_chain=BlockChain()
#     cyber_chain.is_chain_valid()
#     print('Blockchain creata')

# private_key_marco,public_key_marco=get_keys('marco')
# private_key_mario,public_key_mario=get_keys('mario')
# private_key_polo,public_key_polo=get_keys('polo')
# private_key_root,public_key_root=get_keys('root')

# #inizialmente la root trasmette una quantità di moneta agli utenti
# dp1=Transaction(public_key_root,public_key_marco,100)
# dp1.sign_transaction(private_key_root)
# cyber_chain.add_transactions(dp1)
# #cyber_chain.mining_pending_transactions()


# print(cyber_chain.get_balance(public_key_root))
                   
# #inizialmente la root trasmette una quantità di moneta agli utenti
# dp1=Transaction(public_key_root,public_key_marco,100)
# dp1.sign_transaction(private_key_root)
# cyber_chain.add_transactions(dp1)
# cyber_chain.mining_pending_transactions(public_key_mario)                                      
# cyber_chain.content() 

# tx1=Transaction(public_key_marco,public_key_polo,50)
# # #firma di tx1
# tx1.sign_transaction(private_key_marco)
# cyber_chain.add_transactions(tx1)
# cyber_chain.mining_pending_transactions(public_key_mario) 
# cyber_chain.content()
# print(cyber_chain.get_balance(public_key_polo))
# print(cyber_chain.get_balance(public_key_mario))
# print(cyber_chain.get_balance(public_key_marco))
# print(cyber_chain.get_balance(public_key_root))

#cyber_chain.chain[1].transactions[0].amount=200
#cyber_chain.is_chain_valid()

