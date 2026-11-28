# Réponse 1:
# Réponse 2:
# Réponse 3: 
# Réponse 5: 
# Réponse 6: En plus de la r ponse textuelle, ajouter le code 


from ecdsa import SigningKey, NIST384p
import hashlib
class Block:
    
    def __init__(self, previous_block_hash, transaction_list):

        self.previous_block_hash = previous_block_hash
        self.transaction_list = transaction_list

        self.block_data = f"{' - '.join(transaction_list)} - {previous_block_hash}"
        self.block_hash = hashlib.sha256(self.block_data.encode()).hexdigest()
        
class Blockchain:
    def __init__(self):
        self.chain = []
        self.generate_genesis_block()

    def generate_genesis_block(self):
        self.chain.append(Block("0", ['Genesis Block']))
    
    def create_block_from_transaction(self, transaction_list):
        previous_block_hash = self.last_block.block_hash
        self.chain.append(Block(previous_block_hash, transaction_list))

    def display_chain(self):
        for i in range(len(self.chain)):
            print(f"Data {i + 1}: {self.chain[i].block_data}")
            print(f"Hash {i + 1}: {self.chain[i].block_hash}\n")

    @property
    def last_block(self):
        return self.chain[-1]


t1 = "L'employeur me verse 2000 €"
t2 = "J'ai dépensé 70 € chez Total"
t3 = "J'ai dépensé 5 € chez amazone"
t4 = "J'ai dépensé 100 € chez Auchan"
t5 = "J'ai dépensé 110 € chez Engi"
t6 = "J'ai dépensé 30 € chez SFR"

myblockchain = Blockchain()
myblockchain.create_block_from_transaction([t1])
myblockchain.create_block_from_transaction([t2])
myblockchain.create_block_from_transaction([t3])
myblockchain.create_block_from_transaction([t4])
myblockchain.create_block_from_transaction([t5])
myblockchain.create_block_from_transaction([t6])

myblockchain.display_chain()