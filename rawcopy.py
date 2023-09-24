from audioop import add
import errno
import hashlib
import json
from typing import List
from datetime import datetime as dt
from urllib.parse import urlparse
import requests
from random import randint
# from largeprime import toret, find_generator, generate_large_prime

# from blockchain.main import delegates


class Blockchain(object):
    def __init__(self):
        self.chain = []  # list for storing the full blockchain after mining

        # list for storing the transactions which need to be added to the block
        self.unverified_txn = []

        self.verified_txn = []  # list of all the transaction verified till now

        # set of nodes i.e the miners / computers for mining/verificiation of blocks
        self.nodes = set()

        self.all_nodes = []  # list of all nodes

        self.vote_grp = []  # the voting group consisting of all the nodes

        self.star_grp = []  # the group sorted in decreasing order of voting power

        self.super_grp = []  # final group selected for delegates

        self.delegates = []  # the delegates nodes of the blockchain

        self.txn_hashes = []  # hash values of all the transactions

        self.unverified_hash = []  # list of unverified hashes

        self.txns_seller = []  # list of all the transactions
        self.txns_buyer = []

        self.mapping = {}

        self.add_block(
            previous_hash="0x4cd1e910c3d74780000000000000000000000000000000000000000000000000")

    # includes timestamp, previous_hash and merkle root as a part of block header
    def add_block(self, previous_hash):
        txn_hash_adding = self.test()
        hashh = self.conv(txn_hash_adding, previous_hash)
        now = dt.now()
        if len(self.chain) == 0:
            x = "0x4cd1e910c3d74780000000000000000000000000000000000000000000000000"
        else:
            y = self.last_block()
            x = y['hash']
        block_info = {'index': len(self.chain) + 1,  # represnts index of block (position with 1 indexing) in linear blockchain
                 'timestamp': now.strftime("%d/%m/%Y %H:%M:%S"),
                 'transactions': self.unverified_txn,
                 'merkle_root': txn_hash_adding,  # list of transactions corresponding to the block
                 'hash': hashh,
                 'previous_hash': x,

                 }
        self.chain.append(block_info)
        # current list of unverified transactions verified, therefore emptied unverified transactions
        self.unverified_txn = []
        self.unverified_hash = []
        return block_info

    def test(self):
        elems = self.unverified_hash
        mtree = MerkleTree(elems)
        print(elems)
        return mtree.getRootHash()

    def validate_txn(self):  # unverifed transactions corresponding to a block are verified
        
            for i in range(len(self.unverified_txn)):
                prop_id = self.unverified_txn[i]['Property ID']
                sell_id_prop= self.unverified_txn[i]['Seller ID']
                sell_id = self.mapping[prop_id]
                
                p = generate_large_prime(20)
                g  = find_generator(p)
                x = prop_id
                y = pow(g,x)%p
                r = randint(0,p-2)
                h = pow(g,r)%p 
                b = randint(0,1)
                s = (r+b*x)%(p-1)
                alice = pow(g,s)%p
                bob  = (h*pow(y,b))%p
                if(alice == bob and sell_id == sell_id_prop):       
                    self.verified_txn.append(self.unverified_txn[i])
        
    def conv(self,txn,prev):
        an_integer = int(txn, 16)
        an_integer2 = int(prev, 16)
        ans = an_integer ^ an_integer2 ^ 11011110111111111
        hex_value = hex(ans)
        return hex_value
    

    def new_txn(self, buyer_ID,seller_ID, property_ID, rent): #new transaction data for a particular property 
        now = dt.now()
        x = randint(1,1000)
        y = randint(2000,3000)
        self.mapping[property_ID] = seller_ID
        print(self.mapping)
        txn_info={
            'Transaction ID': x^y ,
            'Buyer ID': buyer_ID,
            'Seller ID': seller_ID,
            'Property ID': property_ID,
            'Amount': rent,
            'timestamp': now.strftime("%d-%m-%Y %H:%M:%S")
        }
        self.unverified_txn.append(txn_info)
        txn_hash_curr = self.calc_hash_txns(txn_info)
        self.unverified_hash.append(txn_hash_curr)
        
        # return self.last_block['index'] + 1

    
    def calc_hash(self, block_info): #hash calculated using SHA256 
        block_string = json.dumps(block_info.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def calc_hash_txns(self, txn_info): # hash calculated for transactions as well for merkle root implementation
        block_string = json.dumps(txn_info, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def show_seller(self, prop_ID): #list of transactions sorted by timestamp, corresponding to a particular PROPERTY_ID
        for i in range(len(self.verified_txn)):
            if self.verified_txn[i]['Seller ID'] == prop_ID:
                self.txns_seller.append(self.verified_txn[i])
        return self.txns_seller
    
    def show_buyer(self, prop_ID1): #list of transactions sorted by timestamp, corresponding to a particular PROPERTY_ID
        for i in range(len(self.verified_txn)):
            if self.verified_txn[i]['Buyer ID'] == prop_ID1:
                self.txns_buyer.append(self.verified_txn[i])
        return self.txns_buyer

    def last_block(self): # most recently added block
        return self.chain[-1]
    
    def is_chain_valid(self): # checking if every next block stores the correct "previous block hash"
        prev_block = self.chain[0]
        pos = 1
        if(len(self.chain) == 1):
            return True
        while pos<len(self.chain):
            block = self.chain[pos]
            if(block['previous_hash']!=prev_block['hash']):
                return False 
            prev_block = self.chain[pos]
            pos=pos+1
            
        return True
    
    
    def add_node(self, address, stake):
        parsed_url = urlparse(address)
        authority = stake
        self.nodes.add((parsed_url.netloc,authority))
         
    def voting_power(self): #adding voting for DPOS consensus algorithm by multiplying stake by a random value between 0 and 10
        self.all_nodes = list(self.nodes)
        for x in self.all_nodes:
            votepow= list(x)
            votepow.append(x[1]*randint(1,10))
            self.vote_grp.append(votepow)
            
        # print(self.vote_grp)
        
    def delegates_selection(self):
        self.delegates=[]
        self.star_grp = sorted(self.vote_grp, key = lambda vote: vote[2],reverse = True)
        # print(self.star_grp)

        for x in range(3): # maximum of 3 delegates selected
            self.super_grp.append(self.star_grp[x])
        # print(self.super_grp)

        for y in self.super_grp:
            if(y[0] not in self.delegates):
                self.delegates.append(y[0])
            
        print(self.delegates)
        
    # def resolve_chain(self):
    #     neighbours = self.nodes
    #     new_chain = None
    #     max_length = len(self.chain)

    #     for node in neighbours: 
    #         response = requests.get(f'http://{node}/chain')
        
    #         if response.status_code == 200:
    #             length = response.json()['length']
    #             chain = response.json()['chain']
        
    #             if length > max_length and self.is_chain_valid(chain):
    #                 max_length = length
    #                 new_chain = chain
        
    #     if new_chain:
    #         self.chain = new_chain
    #         return True

    #     return False    
   
    
    def broadcast(self):
        r = requests.get('http://localhost:5000/show/delegates')
        print(r)

        if(r.status_code == 200):
            delegates = r.json()['delegates']
            self.delegates = delegates[0:3]
            print(self.delegates)
            


class Merkle_Node:
    def __init__(self, left, right, value: str, content, is_copied=False) -> None:
        self.left: Merkle_Node = left
        self.right: Merkle_Node = right
        self.value = value
        self.content = content
        self.is_copied = is_copied

    @staticmethod
    def hash(val: str) -> str:
        return hashlib.sha256(val.encode('utf-8')).hexdigest()

    def __str__(self):
        return (str(self.value))

    def copy(self):
        """
        class copy function
        """
        return Merkle_Node(self.left, self.right, self.value, self.content, True)


class MerkleTree: #Merkle tree to use merkle root as a block header attribute
    def __init__(self, values: List[str]) -> None:
        self.__build_MT(values)

    def __build_MT(self, values: List[str]) -> None:

        leaves: List[Merkle_Node] = [Merkle_Node(None, None, Merkle_Node.hash(e), e) for e in values]
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1].copy())  # duplicate last elem if odd number of elements
        self.root: Merkle_Node = self.__buildRecursiveT(leaves)

    def __buildRecursiveT(self, nodes: List[Merkle_Node]) -> Merkle_Node:
        if(len(nodes)==0):
            return
        if len(nodes) % 2 == 1:
            nodes.append(nodes[-1].copy())  # duplicate last elem if odd number of elements
        half: int = len(nodes) // 2

        if len(nodes) == 2:
            return Merkle_Node(nodes[0], nodes[1], Merkle_Node.hash(nodes[0].value + nodes[1].value), nodes[0].content+"+"+nodes[1].content)

        left: Merkle_Node = self.__buildRecursiveT(nodes[:half])
        right: Merkle_Node = self.__buildRecursiveT(nodes[half:])
        value: str = Merkle_Node.hash(left.value + right.value)
        content: str = f'{left.content}+{right.content}'
        return Merkle_Node(left, right, value, content)

    def printTree(self) -> None:
        self.__printRecursiveT(self.root)

    def __printRecursiveT(self, node: Merkle_Node) -> None:
        if node != None:
            if node.left != None:
                print("Left: "+str(node.left))
                print("Right: "+str(node.right))
            else:
                print("Input")
                
            if node.is_copied:
                print('(Padding)')
            print("Value: "+str(node.value))
            print("Content: "+str(node.content))
            print("")
            self.__printRecursiveT(node.left)
            self.__printRecursiveT(node.right)

    def getRootHash(self) -> str:
        if(self.root == None):
            return "0"
        print(self.root)
        return self.root.value # Hash value calculated from all transactions in the block used as the root hash