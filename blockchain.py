from collections import defaultdict
from datetime import datetime
import hashlib
import rsa
import random
from random import randint
import qrcode
import enum
from typing import Any,TypedDict,Literal
from collections.abc import Iterable
"""
Represents the types a node can be
"""

class NodeType(enum.Enum):
  MANUFACTURER = 'manufacturer'
  DISTRIBUTOR = 'distributor'
  CLIENT = 'client'

class NodePublicInfo(TypedDict):
  id: int
  stake: int
  stock: set
  type: NodeType
  public_key: rsa.PublicKey

"""
Represents a Node in the Blockchain (A Node object is private to each running node)
**Fields**
  <in>stake: stake of the node in the system (positive integer)
  <in>id: unique id of the node (positive integer, less than 53 digits) - specifies the port address number of the node on local host, higher port number => earlier the node joined the chain
  <in>stock: dictionary of all product_id the Node has
  <in>type: type of the node (see NodeType)
  public_key, __private_key: the public and private keys of the node
**Methods**
  sign: return the digital signature of the given data for this node
  verify: verifies a signature
"""
class Node():
  def __init__(self,  stake: int, id: int, stock: Iterable[int], type: NodeType) -> None:
    self.stake = stake
    self.id = id
    self.stock = set(stock)
    self.type = type
    self.public_key, self.__private_key = rsa.newkeys(512)

  """
  params:
    data: data to create signature for - lenght < 53
  returns: the created signature (in utf-8)
  """
  def sign(self, data: Any) -> bytes:
    data = str(data)
    return rsa.sign(data.encode('utf-8'), self.__private_key, 'SHA-1')

  """
  params:
    message: data to verify signature for
    signature: signature as a string (utf-8 decoded)
    key: the public key of the node whose signature it is
  returns: True | False
  """
  @staticmethod
  def verify(message: Any, signature: bytes, key: rsa.PublicKey) -> bool:
    return rsa.verify(str(message).encode('utf-8'), signature, key) == 'SHA-1'

  """
  returns: publically available data of this node, the stock set's reference is returned, changing stock returned by getInfo, changes
  """
  def getInfo(self) -> NodePublicInfo:
    return {
      'id': self.id,
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
  def __init__(self, manufacturer_id: int, product_id: int, sender_id: int, receiver_id: int, sender_sign: bytes) -> None:
    self.manufacturer_id = manufacturer_id
    self.product_id = product_id
    self.sender_id = sender_id
    self.receiver_id = receiver_id
    self.timestamp = datetime.now().strftime("%d|%m|%Y><%H:%M:%S")
    self.transaction_id = receiver_id^product_id^sender_id
    self.sender_sign: bytes = sender_sign
    self.receiver_sign: None | bytes = None
  
  def  __str__(self):
    return str(self.__dict__)
  
"""
Represents a Block of the blockchain
**Fields**
  previous_hash: hash of the header of the previous block
  merkle_tree: the merkle tree of this block (the merkle nodes are read only)
  merkle_root: merkle tree root hash value (read-only)
  height: block height on the blockchain
  miner_id: miner responsible for adding this block
  timestamp: timestamp when the block was mined
  header_hash: hash of the header of this block (except the header hash itself)
  transactions: transactions in the block
"""
class Block():
  def __init__(self, prev_hash: str, height: int, transactions:Iterable[Transaction], miner_id: int) -> None:
    self.previous_hash = prev_hash
    # the merkle tree and root are read only after creation
    self.merkle_tree = MerkleTree(transactions)
    self.height = height
    self.miner_id = miner_id
    self.timestamp = datetime.now()
    self.header_hash = Blockchain.calculateHash(prev_hash + self.merkle_root + str(height) + str(miner_id) + self.timestamp.strftime("%d|%m|%Y><%H:%M:%S"))
    self.transactions:list[Transaction] = list(transactions)

  """
  read-only property merkle_root
  """
  @property  
  def merkle_root(self):
    return self.merkle_tree.getRootHash()
  
  def __str__(self) -> str:
    return str(self.__dict__)

"""
Represents the Blockchain copy on a node
**Fields**
  manufacturer: manufacturer for this supply chain management
  blockchain: dictionary containing all blocks in this blockchain copy (header_hash as key)
  nodes: dictionary containing all known nodes public info (id as key)
  pending_transactions: dictinary containing all transactions yet to be accepted by the second party (receiver_id as key)
  accepted_transactions: list of transactions accepted by both participating nodes,    not verified
  newest_block: header_hash of the latest block added to the chain
  parent_node: the node running this blockchain copy
**Methods**
  mineBlock: verify transactions of a block, the block itself and add it to the blockchain, miner and validators chosen based on consensus algorithm (contains the voting function to simulate a round of voting)
  ! consensus algorithm runs here
  validateTransactions: validate a goven transaction
  validateBlock: validate a given block
  requestTransaction: the parent node sends product id to a receiver node; manufacturer can make a transaction to itself to add products to the supply chain
  getPendingTransactions: parent node prints the transactions waiting for its signature
  accept | reject Transaction: parent node accepts | rejects an incoming transaction request
  changeParentNode: make another node parent
  calculate_hash: utility function to find SHA-256 hash of some data
  getProductStatus: given a product id, traverse the block chain to find the most recent transaction the product was present in
"""
class Blockchain():
  def __init__(self, manufacturer_node: Node) -> None:
    current_active_nodes[manufacturer_node.id] = manufacturer
    self.manufacturer_id = manufacturer_node.id
    # header_hash => block
    self.blockchain: dict[str, Block] = dict()
    genesis_block = Block(self.calculateHash(''), 0, [], manufacturer_node.id)
    self.blockchain[genesis_block.header_hash] = genesis_block
    # node_id => node's public info
    self.nodes: dict[int, NodePublicInfo] = {manufacturer_node.id: manufacturer_node.getInfo()}
    # the genesis block
    self.blocked_nodes: set[int] = set()
    # receiver_id => unsigned transaction list
    self.pending_transactions: dict[int, list[Transaction]] = defaultdict(list)
    self.accepted_transactions: list[Transaction] = []
    self.newest_block = genesis_block.header_hash
    self.parent_node = manufacturer_node

  
  def mineBlock(self) -> None:
    print("Mining initiated")
    def voting() -> tuple[int, int, int]:
      # selection of validators: [stake, id] - assume all active nodes available for mining and validation
      node_stake: list[list[int]] = [[node['stake']+len(node['stock']), id] for id, node in self.nodes.items()]

      # less than 3 nodes in the chain
      if(len(node_stake)==1):
          return node_stake[0][1], node_stake[0][1], node_stake[0][1]
      if(len(node_stake)==2):
          return node_stake[0][1], node_stake[0][1], node_stake[1][1]
    
         
      delegates:list[list[int,int]]=random.choices(node_stake,k=3)
      print('list of chosen delegates \n')
      print(delegates)
      print('\n')
      print('stakes before voting \n')
      for x in node_stake:
        print(x[1],x[0],sep='-')

      print('\n')  
      for x in node_stake:
            
            if x in delegates:
              continue

            value=x[0]
            selection=random.choice(delegates)
            selection[0]+=value

      print('Nodes\' vote values after voting round (id, voting power):', [(id, vp) for vp, id in node_stake]) 
      # if two nodes have the same vote values, compare their ids (higher id => older node)
      delegates.sort(reverse=True)
      return delegates[0][1], delegates[1][1], delegates[2][1]

    miner, validator1, validator2 = voting()
    print('Chosen Miner id:', miner, 'Chosen Validator ids:', validator1, validator2)
    
    block_txn = self.accepted_transactions
    # verify all accepted transactions
    for txn in block_txn.copy():
      if not self.validateTransaction(txn):
        block_txn.remove(txn)
    # if there are no transactions, stop mining
    if not block_txn:
      self.accepted_transactions.clear()
      self.blocked_nodes.clear()
      return print("No valid transactions for this block found")

    print("Valid transactions separated:", block_txn)
    new_block = Block(self.newest_block, len(self.blockchain), block_txn, miner)

    if not self.validateBlock(new_block):
      print("Block failed verification for 50% validators, applying penalty to the miner")
      self.nodes[miner]['stake'] //= 2
      # BROADCAST
      current_active_nodes[miner].stake //= 2
      return
    
    print('rewarding miner and validators')
    self.nodes[miner]['stake'] += 2
    self.nodes[validator1]['stake'] += 2
    self.nodes[validator2]['stake'] += 2
    # BROADCAST
    current_active_nodes[miner].stake += 2
    current_active_nodes[validator1].stake += 2
    current_active_nodes[validator2].stake += 2

    # Block is valid, make necessary changes to the blockchain
    self.accepted_transactions.clear()
    self.blocked_nodes.clear()
    self.blockchain[new_block.header_hash]=new_block
    self.newest_block=new_block.header_hash

  """
  Validate a transaction and perform the operations if it is valid; only manufacturer can make a transaction to oneself
  """
  def validateTransaction(self, transaction:Transaction) -> bool:
    self.blocked_nodes.remove(transaction.sender_id)
    if transaction.receiver_id != transaction.sender_id:
      self.blocked_nodes.remove(transaction.receiver_id)
    if Node.verify(transaction.transaction_id, transaction.sender_sign, self.nodes[transaction.sender_id]['public_key']) and transaction.receiver_sign:
      print("sender_sign verified")
      if Node.verify(transaction.transaction_id, transaction.receiver_sign, self.nodes[transaction.receiver_id]['public_key']):
        print("reciever_sign verified")
        if transaction.sender_id == transaction.receiver_id:
          print('transaction from manufacturer to manufacturer')
          if transaction.sender_id != transaction.manufacturer_id:
            print("Transaction to oneself (not manufacturer) detected")
            return False
          # Manufacturer adds products to the blockchain
          self.nodes[transaction.receiver_id]['stock'].add(transaction.product_id)
          # BROADCAST
          current_active_nodes[transaction.receiver_id].stock.add(transaction.product_id)
          return True
        elif transaction.product_id in self.nodes[transaction.sender_id]['stock']:
          print('Product id in sender\'s stock verified')
          # perform the transaction operations
          self.nodes[transaction.sender_id]['stock'].remove(transaction.product_id)
          self.nodes[transaction.receiver_id]['stock'].add(transaction.product_id)
          return True
        else:
          # double spending detected
          print("Double Spending by id:", transaction.sender_id, "detected")
          print("Penalizing the node")
          self.nodes[transaction.sender_id]['stake'] //= 2
          current_active_nodes[transaction.sender_id].stake //= 2
    return False
  
  def validateBlock(self, block: Block) -> bool:
    # check the merkle tree
    temp_tree=MerkleTree(block.transactions)
    if not (temp_tree.getRootHash()==block.merkle_root):
      return False
    
    print("merkle tree verified")
    # check the previous hash and the block height
    if not (block.previous_hash in self.blockchain) or not (self.blockchain[block.previous_hash].height==block.height-1):
      return False
    
    print('previous hash verified')
    # check the headerhash
    header_hash=self.calculateHash(block.previous_hash + block.merkle_root + str(block.height) + str(block.miner_id) + block.timestamp.strftime("%d|%m|%Y><%H:%M:%S"))
    if not header_hash==block.header_hash:
      return False
    
    print('header hash verified')
    print('block verified')
    # block verified
    return True

  def startTransaction(self, receiver_id: int, product_id: int) -> None:
    sender_id = self.parent_node.id
    if self.parent_node.id in self.blocked_nodes: return print("Previous transaction verification pending.\n Next transaction can be requested only after verifying previous one")
    new_txn = Transaction(self.manufacturer_id, product_id, sender_id, receiver_id, self.parent_node.sign(product_id^sender_id^receiver_id))
    if sender_id == receiver_id == self.manufacturer_id:
      new_txn.receiver_sign = self.parent_node.sign(new_txn.transaction_id)
      self.accepted_transactions.append(new_txn)
      self.blocked_nodes.add(receiver_id)
      return print("Given product will be added in next mining")
    self.pending_transactions[receiver_id].append(new_txn)
    self.blocked_nodes.add(sender_id)
    print("Transaction request sent to: ", receiver_id)
    return print("Transaction id:", new_txn.transaction_id)

  def getPendingTransactions(self) -> list[str]:
    return [str(txn) for txn in self.pending_transactions[self.parent_node.id]]
  
  """
  Reject a transaction, the initiator is notified and removed from blocked_nodes
  """
  def rejectTransactionRequest(self, sender_id: int) -> None:
    for txn in self.pending_transactions[self.parent_node.id]:
      if txn.sender_id == sender_id:
        self.pending_transactions[self.parent_node.id].remove(txn)
        self.blocked_nodes.remove(txn.sender_id)
        return print("Transaction rejected")
    return print("No such transaction")
  
  """
  Delete a transaction started by the parent_node
  """
  def deletePendingTransaction(self, receiver_id: int) -> None:
    for txn in self.pending_transactions[receiver_id]:
      if txn.sender_id == self.parent_node.id:
        self.pending_transactions[receiver_id].remove(txn)
        self.blocked_nodes.remove(self.parent_node.id)
        return print("Transaction Request")
    return print("No such transaction")


  """
  Accept a transaction, the acceptor is added to the blocked_nodes list, transaction moved to accepted_transactions
  """
  def acceptTransaction(self, sender_id: int) -> None:
    if self.parent_node.id in self.blocked_nodes: return print("Previous transaction verification pending.\n Next transaction can be accepted only after verifying previous one")
    for txn in self.pending_transactions[self.parent_node.id]:
      if txn.sender_id == sender_id:
        self.pending_transactions[self.parent_node.id].remove(txn)
        txn.receiver_sign = self.parent_node.sign(txn.transaction_id)
        self.accepted_transactions.append(txn)
        self.blocked_nodes.add(self.parent_node.id)
        return print("Transaction accepted")
    return print("No such transaction")
    
  def changeParentNode(self, node_id: int) -> None:
    self.parent_node = current_active_nodes[node_id]

  @staticmethod
  def calculateHash(s: Any) -> str:
    return hashlib.sha256(str(s).encode()).hexdigest()
  
  def addNode(self, n_address: int, initial_stake: int, type: Literal['client', 'distributor'], n_stock: Iterable[int] = ()) -> None:
    if type == 'client':
      ntype = NodeType.CLIENT
    else:
      ntype = NodeType.DISTRIBUTOR
    new_node = Node(10*initial_stake, n_address, n_stock, ntype)
    self.nodes[new_node.id] = new_node.getInfo()
    # BROADCAST
    current_active_nodes[new_node.id] = new_node
  
  def getProductStatus(self, product_id: int) -> str:
    ans:str
    cur_block = self.blockchain[self.newest_block]
    while cur_block.height != 0:
      for txn in cur_block.transactions:
        if txn.product_id == product_id:
          if txn.sender_id_id == txn.manufacturer_id == txn.receiver_id:
            ans= "Manufacturer with id: " + str(self.manufacturer_id) + " added the product to the supply chain on: " + txn.timestamp
          ans= "Product with id: " + str(product_id) + " was sent from: " + self.nodes[txn.sender_id]['type'].name + " id: " + str(txn.sender_id) + " to: " + self.nodes[txn.receiver_id]['type'].name + " id: " + str(txn.receiver_id) + " on: " + txn.timestamp
    ans= "Product does not exist on the supply chain"
    img = qrcode.make(ans)
    img.save('MyQRCode1.png')

"""
Class defining a node of the merkle tree
**Fields**
  left: the left child
  right: the right child
  value: hash stored at this node (read-only after creation)
"""
class MerkleNode():
  def __init__(self, value: str, left = None, right = None) -> None:
    self.left: None | MerkleNode = left
    self.right: None | MerkleNode = right
    self.__value = value
  
  @property
  def value(self) -> str:
    return self.__value
    
"""
Class defining a merkle tree
**Fields**
  tree_root: the root of the merkle tree
"""
class MerkleTree():
  def __init__(self, transactions: Iterable[Transaction]) -> None:
    # empty hash for empty input
    self.tree_root: MerkleNode = self.__buildTree([MerkleNode(Blockchain.calculateHash(txn)) for txn in transactions]) if transactions else MerkleNode('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')

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

# pool of all active nodes
current_active_nodes: dict[int, Node] = dict()

######      Testing Zone      ######
if __name__ == '__main__':

  manufacturer = Node(10000, 9999, (123, 321, 111, 222, 333), NodeType.MANUFACTURER)
  bc = Blockchain(manufacturer)
  print("add distributor 9998")
  bc.addNode(9998, 1000, 'distributor', (323,))
  print('add distributor 9997')
  bc.addNode(9997, 1100, 'distributor', (909,))
  print("add client 9996")
  bc.addNode(9996, 100, 'client', ())
  print([node.getInfo() for node in current_active_nodes.values()])
  print(bc.nodes)
  # manufacturer starts a transaction with the distributor
  bc.startTransaction(9998, 123)
  # distributor starts a transaction with the client
  bc.changeParentNode(9997)
  bc.startTransaction(9997, 323)
  print(bc.pending_transactions)
  print("Now at node: ", bc.parent_node.getInfo())
  print("Pending transacs for 9998:", bc.getPendingTransactions())
  # distributor accepts the transac
  bc.acceptTransaction(9999)
  print(bc.pending_transactions)
  # transacs are verified in next mining
  bc.mineBlock()
  # print blockchain
  cur_block = bc.newest_block
  while bc.blockchain[cur_block].height != 0:
    print(bc.blockchain[cur_block])
    cur_block = bc.blockchain[cur_block].previous_hash
  print(bc.blockchain[cur_block])
