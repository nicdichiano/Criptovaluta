from ecdsa import SigningKey,VerifyingKey,SECP256k1
import sys

def generate_key(owner):
    private_key=SigningKey.generate(SECP256k1)
    public_key=private_key.get_verifying_key()
    private_key=private_key.to_string().hex()
    public_key=public_key.to_string().hex()

    #memorizzo le chiavi in un file utilizzando la variabile output
    output= f"""
private_key: {private_key}
public_key: {public_key}
    """
    textfile=open('keys_'+owner,'w')
    textfile.write(output)
    textfile.close()

    indirizzi=open('indirizzi','a')
    output2=f"""
public_key: {public_key}   
    """
    indirizzi.write(output2)
    indirizzi.close()


if __name__=='__main__':
    generate_key(sys.argv[1])   #permette di chiamare la funzione in questo modo: generate_key.py mario


