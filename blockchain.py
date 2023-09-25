from collections import defaultdict
from datetime import datetime
import hashlib
from numpy import block
import rsa
import random
from random import randint
import enum
from typing import Any
from collections.abc import Iterable
"""
Represents the types a node can be
"""
class NodeType(enum.Enum):
  MANUFACTURER = 'manufacturer'
  DISTRIBUTOR = 'distributor'
  CLIENT = 'client'

"""
Represents a Node in the Blockchain (A Node object is private to each running node)
**Fields**
  address: address to communicate with this node
  stake: stake of the node in the system (positive integer)
  id: unique id of the node (positive integer, less than 53 digits)
  stock: dictionary of all product_id the Node has
  type: type of the node (see NodeType)
  public_key, __private_key: the public and private keys of the node
**Methods**
  sign: return the digital signature of the given data
"""
class Node():
  def __init__(self, address: str, stake: int, id : int, stock: Iterable[int], type: NodeType) -> None:
    self.address = address
    self.stake = stake
    self.id = id
    self.stock = set(stock)
    self.type = type
    self.public_key, self.__private_key = rsa.newkeys(512)

  # For too large data, return None as error (size limit: 53)
  def sign(self, data: Any) -> str:
    data = str(data)
    return rsa.sign(data.encode('utf-8'), self.__private_key, 'SHA-1').decode('utf-8')

  def getInfo(self) -> dict[str, Any]:
    return {
      'address': self.address,
      'stake': self.stake,
      'stock': self.stock,
      'type': self.type,
      'public_key': self.public_key
    }

"""
Represents a transaction in the blockchain
**Fields**
  manufacturer_id, sender_id, receiver_id, product_id: are the respective unique ids
  timestamp: timestamp when the trasaction was started
  transaction_id: semi-unique id for signing of the transaction
  sender_sign: digital signature of the sender using transaction_id
  receiver_sign: digital signature of the receiver using transaction_id
> a node signs the transaction if it accepts it
**Methods**
  str: returns a str version of the transaction for hashing
"""
class Transaction():
  def __init__(self, manufacturer_id: int, product_id: int, sender_id: int, receiver_id: int, sender_sign: str) -> None:
    self.manufacturer_id = manufacturer_id
    self.product_id = product_id
    self.sender_id = sender_id
    self.receiver_id = receiver_id
    self.timestamp = datetime.now().strftime("%d|%m|%Y><%H:%M:%S")
    self.transaction_id = receiver_id^product_id^sender_id
    self.sender_sign: str = sender_sign
    self.receiver_sign: None | str = None
  
  def  __str__(self):
    return str(self.__dict__)
  
"""
Represents a Block of the blockchain
**Fields**
  previous_hash: hash of the header of the previous block
  merkle_root: merkle tree root hash value
  height: block height on the blockchain
  miner_id: miner responsible for adding this block
  timestamp: timestamp when the block was mined
  header_hash: hash of the header of this block (except the header hash itself)
  transactions: transactions in the block
"""
class Block():
  def __init__(self, prev_hash: str, height: int, transactions:Iterable[Transaction], miner_id: int) -> None:
    self.previous_hash = prev_hash
    merkle_tree = MerkleTree(transactions)
    self.__merkle_root = merkle_tree.getRootHash()
    self.height = height
    self.miner_id = miner_id
    self.timestamp = datetime.now()
    self.header_hash = Blockchain.calculateHash(prev_hash + self.merkle_root + str(height) + str(miner_id) + self.timestamp.strftime("%d|%m|%Y><%H:%M:%S"))
    self.transactions = transactions

  @property  
  def merkle_root(self):
    return self.__merkle_root

"""
Represents the Blockchain copy on a node
**Fields**
  manufacturer: manufacturer for this supply chain management
  blockchain: dictionary containing all blocks in this blockchain copy (header_hash as key)
  nodes: dictionary containing all known nodes public info (id as key)
  pending_transactions: dictinary containing all transactions yet to be accepted by the second party (receiver_id as key)
  TODO
  accepted_transactions: list of transactions accepted by both participating nodes <verified?>
  newest_block: header_hash of the latest block added to the chain
  parent_node: the node running this blockchain copy
**Methods**
  requestTransaction: the parent node sends product id to a receiver node
  checkPendingTransactions: parent node prints the transactions waiting for its signature
  accept|reject Transaction: parent node accepts | rejects an incoming transaction request
  changeParentNode: make another node parent
  calculate_hash: utility function to find SHA-256 hash of some data
  TODO
  mine_block: <verify?> transactions of a block and add it to the blockchain
  ! consensus algorithm runs here
"""
# TODO: Remove parent_node concept if not feasible
class Blockchain():
  def __init__(self, manufacturer_id: int, manufacturer_info: dict[str, Any], parent_node: Node) -> None:
    self.manufacturer_id = manufacturer_id
    self.blockchain: dict[str, Block] = dict()
    self.nodes: dict[int, dict[str, Any]] = {manufacturer_id: manufacturer_info}
    genesis_block = Block(self.calculateHash(''), 0, [], manufacturer_id)
    self.blockchain[genesis_block.header_hash] = genesis_block
    self.blocked_nodes: set[int] = set()
    self.pending_transactions: dict[int, list[Transaction]] = defaultdict(list)
    self.accepted_transactions: list[Transaction] = []
    self.newest_block = genesis_block.header_hash
    self.parent_node = parent_node

  
  def mine_block(self) -> None:
    # selection of validators, (stake, id)
    current_stake: list[tuple[int, int]] = [(node['stake']+len(node['stock']) + random.randint(1, 100), id) for id, node in self.nodes.items()]

    def voting(node_stakes: list[list[int, int]]) -> list[int, int]:
      # less than 2 nodes validator1 = validator2
      if(node_stakes.Len()==1):
          return node_stakes[0][1], node_stakes[0][1]
      
      if(node_stakes.Len()==2):
          return node_stakes[0][1], node_stakes[1][1]
         
      delegates:list[list[int,int]]=random.choices(node_stakes,k=3)
     
      dummy=delegates.copy()
      for x in delegates:
            value=x[0]
            selection=random.choice(node_stakes)[1]
            x[0]=0
            for y in dummy:
              if y[1]==selection:
                y[0]+=value
              

      dummy.sort(reverse=True)
      return dummy[0][1], dummy[1][1]
    

    validator1, validator2 = voting(current_stake)

  
  def validateBlock(self, block: Block) -> bool:
    pass
    return True

  def broadcast(self) -> None:
    # send the current status of the BC to all listening nodes
    pass


  def requestTransaction(self, receiver_id: int, product_id: int) -> None:
    sender_id = self.parent_node.id
    if self.parent_node.id in self.blocked_nodes: return print("Previous transaction verification pending.\n Next transaction can be requested only after verifying previous one")
    new_txn = Transaction(self.manufacturer_id, product_id, sender_id, receiver_id, self.parent_node.sign(product_id^sender_id^receiver_id))
    self.pending_transactions[receiver_id].append(new_txn)
    self.blocked_nodes.add(receiver_id)
    print("Transaction request sent to: ", receiver_id)
    print("Transaction id:", new_txn.transaction_id)

  def checkPendingTransactions(self) -> None:
    for txn in self.pending_transactions[self.parent_node.id]:
      print("Transaction: ", str(txn))
  
  def rejectTransaction(self, transaction_id: int) -> None:
    for txn in self.pending_transactions[self.parent_node.id]:
      if txn.transaction_id == transaction_id:
        self.pending_transactions[self.parent_node.id].remove(txn)
        return print("Transaction rejected")
    return print("No such transaction")

  def acceptTransaction(self, transaction_id: int) -> None:
    if self.parent_node.id in self.blocked_nodes: return print("Previous transaction verification pending.\n Next transaction can be accepted only after verifying previous one")
    for txn in self.pending_transactions[self.parent_node.id]:
      if txn.transaction_id == transaction_id:
        self.pending_transactions[self.parent_node.id].remove(txn)
        txn.receiver_sign = self.parent_node.sign(transaction_id)
        self.accepted_transactions.append(txn)
        self.blocked_nodes.add(self.parent_node.id)
        return print("Transaction accepted")
    return print("No such transaction")
    
  def changeParentNode(self, node_id: int) -> None:
    self.parent_node = current_active_nodes[node_id]

  @staticmethod
  def calculateHash(s: Any) -> str:
    return hashlib.sha256(str(s).encode()).hexdigest()
  
  def addBlock(self,prev_hash:str):
        timeStamp=datetime.now()
        

class MerkleNode():
  def __init__(self, value: str, left = None, right = None) -> None:
    self.left: None | MerkleNode = left
    self.right: None | MerkleNode = right
    self.value = value
    
class MerkleTree():
  def __init__(self, transactions: Iterable[Transaction]) -> None:
    self.tree_root: MerkleNode = self.__buildTree([MerkleNode(Blockchain.calculateHash(txn)) for txn in transactions])

  def __buildTree(self, transactions: list[MerkleNode]) -> MerkleNode:
    if len(transactions) == 1: 
      return transactions[0]
    else:
      next_level: list[MerkleNode] = []
      if len(transactions) % 2:
        transactions.append(transactions[-1])
      while transactions:
        left = transactions.pop()
        right = transactions.pop()
        next_level.append(MerkleNode(Blockchain.calculateHash(left.value+right.value), left, right))
      return self.__buildTree(next_level)

  def getRootHash(self) -> str:
    return self.tree_root.value

#######  Functions actually called from terminal / users / connected tom api's  #######

# these global variables represent the state of the network, 
current_active_nodes: dict[int, Node] = dict()
global_unique_node_id = 0
global_unique_product_id = 0

def add_node(n_address: str, security_deposit: int, type: NodeType, n_id : int = 0, n_stock: Iterable[int] = ()) -> None:
  if not n_id:
    global global_unique_node_id
    n_id = global_unique_node_id
    global_unique_node_id += 1
  elif n_id in current_active_nodes:
    return print("Node id already in use")
  new_node = Node(n_address, 10*security_deposit, n_id, n_stock, type)
  current_active_nodes[new_node.id] = new_node

# the main function of our code
def startVirtualMachine(m_address: str, m_stake: int, m_id : int, m_stock: Iterable[int]):
  global manufacturer, blockchain
  manufacturer = Node(m_address, m_stake, m_id, m_stock, NodeType.MANUFACTURER)
  current_active_nodes[manufacturer.id] = manufacturer
  blockchain = Blockchain(manufacturer.id, manufacturer.getInfo(), manufacturer)
