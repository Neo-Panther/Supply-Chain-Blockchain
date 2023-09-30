from collections import defaultdict
from datetime import datetime
import hashlib
import rsa
import random
import qrcode
import enum
from typing import Any, TypedDict, Literal
from collections.abc import Iterable
MAX_TRANSACSIZE = 3

"""
Represents the types a node can be
"""
class NodeType(enum.Enum):
  MANUFACTURER = 'manufacturer'
  DISTRIBUTOR = 'distributor'
  CLIENT = 'client'

"""
Data class representing the public info of a node
"""
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
  <in>stock: set of all product_id the Node has
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
  
  def __str__(self) -> str:
    return str(self.__dict__)

"""
Represents a transaction in the blockchain
**Fields**
  manufacturer_id, sender_id, receiver_id, product_ids: are the respective unique ids
  timestamp: timestamp when the trasaction was started
  transaction_id: semi-unique id for signing of the transaction
  sender_sign: digital signature of the sender using transaction_id
  receiver_sign: digital signature of the receiver using transaction_id
> a node signs the transaction if it accepts it
**Methods**
  str: returns a str version of the transaction for hashing
"""
class Transaction():
  def __init__(self, manufacturer_id: int, product_ids: set[int], sender_id: int, receiver_id: int, sender_sign: bytes) -> None:
    self.manufacturer_id = manufacturer_id
    self.product_ids = product_ids
    self.sender_id = sender_id
    self.receiver_id = receiver_id
    self.timestamp = datetime.now().strftime("%d|%m|%Y><%H:%M:%S")
    product_xor = 0
    for i in product_ids:
      product_xor ^= i
    self.transaction_id = receiver_id^product_xor^sender_id
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
  startTransaction: the parent node sends product id to a receiver node; manufacturer can make a transaction to itself to add products to the supply chain
  getPendingTransactions: parent node prints the transactions waiting for its signature
  (accept|reject)TransactionRequest: parent node accepts | rejects an incoming transaction request
  changeParentNode: make another node parent
  calculate_hash: utility function to find SHA-256 hash of some data
  getProductStatus: given a product id, traverse the block chain to find the most recent transaction the product was present in
  showBlockchain: print all blocks of the blockchain
"""
class Blockchain():
  def __init__(self, manufacturer_node: Node) -> None:
    # BROADCAST
    current_active_nodes[manufacturer_node.id] = manufacturer_node
    self.manufacturer_id = manufacturer_node.id
    for product in manufacturer_node.stock:
      product_locations[product] = self.manufacturer_id
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
    voted: defaultdict[int, set[int]] = defaultdict(set)
    def voting() -> tuple[int, int, int]:
      # selection of validators: [stake, id] - assume all active nodes available for mining and validation
      node_stake: list[list[int]] = [[node['stake']+len(node['stock']), id] for id, node in self.nodes.items()]
      mstake = max(node_stake, key=lambda x: x[0])[0]
      for i in node_stake:
        i[0] += random.randint(0, mstake)

      print('Stakes Before Voting (id, stake): ', [(node[1], node[0]) for node in node_stake])

      # less than 3 nodes in the chain
      if(len(node_stake)==1):
          return node_stake[0][1], node_stake[0][1], node_stake[0][1]
      if(len(node_stake)==2):
          return node_stake[0][1], node_stake[0][1], node_stake[1][1]
         
      delegates:list[list[int]]=random.sample(node_stake,k=random.randint(3, len(node_stake) - 1))
      print('List of Chosen Delegates: ', delegates)
      print('Vote Values Before Voting (id, stake): ', [(node[1], node[0]) for node in node_stake])

      for x in node_stake:
        if x in delegates:
          continue
        delegate = random.choice(delegates)
        delegate[0] += x[0]
        voted[delegate[1]].add(x[1])
        x[0] = 0

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
      print("Block failed verification for 50% validators, applying penalty to the miner and those who voted for him")
      self.nodes[miner]['stake'] //= 2
      current_active_nodes[miner].stake //= 2
      for id in voted[miner]:
        self.nodes[id]['stake'] -= 20
        current_active_nodes[id].stake -= 20
    else:    
      print("Block Mined, 2 confirmations received, applying valid transaction operations::")
      for transaction in new_block.transactions:
        if transaction.sender_id == transaction.receiver_id:
          print('Transaction from manufacturer to manufacturer')
        else:
          # perform the transaction operations
          self.nodes[transaction.sender_id]['stock'] = self.nodes[transaction.sender_id]['stock'].difference(transaction.product_ids)
          # BROADCAST
          current_active_nodes[transaction.sender_id].stock = current_active_nodes[transaction.sender_id].stock.difference(transaction.product_ids)
        # receiver always gets the goods
        self.nodes[transaction.receiver_id]['stock'] = self.nodes[transaction.receiver_id]['stock'].union(transaction.product_ids)
        # BROADCAST
        for product in transaction.product_ids:
          product_locations[product] = transaction.receiver_id
        current_active_nodes[transaction.receiver_id].stock = current_active_nodes[transaction.receiver_id].stock.union(transaction.product_ids)
      
      print('Rewarding Miner and his voters')
      self.nodes[miner]['stake'] += 200
      current_active_nodes[miner].stake += 200
      for id in voted[miner]:
        self.nodes[id]['stake'] += 5
        current_active_nodes[id].stake += 5

      # Block is valid, make necessary changes to the blockchain
      self.accepted_transactions.clear()
      self.blocked_nodes.clear()
      self.blockchain[new_block.header_hash]=new_block
      self.newest_block=new_block.header_hash
    
    print("Rewarding validator and their voters::")
    self.nodes[validator1]['stake'] += 20
    current_active_nodes[validator1].stake += 20
    for id in voted[validator1]:
      self.nodes[id]['stake'] += 2
      current_active_nodes[id].stake += 2
    self.nodes[validator2]['stake'] += 20
    current_active_nodes[validator2].stake += 20
    for id in voted[validator2]:
      self.nodes[id]['stake'] += 2
      current_active_nodes[id].stake += 2

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
          if transaction.sender_id != transaction.manufacturer_id:
            print("Transaction to oneself (not manufacturer) detected")
            return False
          return True
        elif not transaction.product_ids.difference(self.nodes[transaction.sender_id]['stock']):
          print('Product id in sender\'s stock verified')
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

  def startTransaction(self, receiver_id: int, product_ids: set[int]) -> None:
    sender_id = self.parent_node.id
    if self.parent_node.id in self.blocked_nodes: return print("Previous transaction verification pending.\n Next transaction can be requested only after verifying previous one")
    product_xor = 0
    for i in product_ids:
      product_xor ^= i
    new_txn = Transaction(self.manufacturer_id, product_ids, sender_id, receiver_id, self.parent_node.sign(product_xor^sender_id^receiver_id))
    self.pending_transactions[receiver_id].append(new_txn)
    if sender_id == receiver_id == self.manufacturer_id:
      self.acceptTransactionRequest(self.manufacturer_id)
      return print("Given products will be added in next mining")
    self.blocked_nodes.add(sender_id)
    print("Transaction request sent to: ", receiver_id)
    print("Transaction id:", new_txn.transaction_id)
    return print("Wait for receiver's response; and the next mining for the transaction to be completed")

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
  Accept a transaction, the acceptor is added to the blocked_nodes list, transaction moved to accepted_transactions
  """
  def acceptTransactionRequest(self, sender_id: int) -> None:
    if self.parent_node.id in self.blocked_nodes: return print("Previous transaction verification pending.\n Next transaction can be accepted only after verifying previous one")
    for txn in self.pending_transactions[self.parent_node.id]:
      if txn.sender_id == sender_id:
        self.pending_transactions[self.parent_node.id].remove(txn)
        txn.receiver_sign = self.parent_node.sign(txn.transaction_id)
        self.accepted_transactions.append(txn)
        self.blocked_nodes.add(self.parent_node.id)
        print("Transaction accepted")
        if len(self.accepted_transactions) >= MAX_TRANSACSIZE:
          print("Multiple unverified transactions in the network")
          print("Other nodes have started mining")
          return self.mineBlock()
        return
    return print("No such transaction for current parent")
    
  def changeParentNode(self, node_id: int) -> None:
    self.parent_node = current_active_nodes[node_id]

  @staticmethod
  def calculateHash(s: Any) -> str:
    return hashlib.sha256(str(s).encode()).hexdigest()
  
  def addNode(self, n_address: int, initial_stake: int, type: Literal['client', 'distributor'], n_stock: set[int] = set()) -> None:
    if type == 'client':
      ntype = NodeType.CLIENT
    else:
      ntype = NodeType.DISTRIBUTOR
    new_node = Node(10*initial_stake, n_address, n_stock, ntype)
    for product in n_stock:
      product_locations[product] = n_address
    self.nodes[new_node.id] = new_node.getInfo()
    # BROADCAST
    current_active_nodes[new_node.id] = new_node
  
  def getProductStatus(self, product_id: int) -> str:
    cur_block = self.blockchain[self.newest_block]
    ans = ""
    while cur_block.height != 0:
      for txn in cur_block.transactions:
        for pid in txn.product_ids:
          if pid == product_id:
            if txn.sender_id == txn.manufacturer_id == txn.receiver_id:
              ans = "Manufacturer with id: " + str(self.manufacturer_id) + " added the product to the supply chain on: " + txn.timestamp
            ans = "Product with id: " + str(product_id) + " was sent from: " + self.nodes[txn.sender_id]['type'].name + " id: " + str(txn.sender_id) + " to: " + self.nodes[txn.receiver_id]['type'].name + " id: " + str(txn.receiver_id) + " on: " + txn.timestamp
      cur_block = self.blockchain[cur_block.previous_hash]
    if not ans:
      ans = "Product does not exist on the Blockchain"
      if product_id in product_locations:
        ans = "Product found with node id: " + str(product_locations[product_id]) + "\nIt has not been used in any transactions"
    img = qrcode.make(ans)
    file_name = 'MyQRCode' + datetime.now().strftime("%d-%m-%Y--%H-%M-%S") + '.png'
    img.save(file_name)
    return file_name

  def showBlockchain(self) -> None:
    print("###  Printing Blocks in the Blockchain  ###")
    cur_block = self.blockchain[self.newest_block]
    while cur_block.height != 0:
      print(cur_block)
      cur_block = self.blockchain[cur_block.previous_hash]
    return print(cur_block)

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

# tracks used product ids and their current locations
product_locations: dict[int, int] = dict()

if __name__ == '__main__':
  print("Creating Blockchain")
  print("Enter initial products with manufacturer::")
  stock = {1, 2}
  manufacturer = Node(100000000, 9999, stock, NodeType.MANUFACTURER)
  print("Manufacturer Node successfully created")
  print("Node public info broadcasted to all nodes: ", manufacturer.getInfo())
  bc = Blockchain(manufacturer)
  print("Blockchain Created")
  address = 9998
  bc.addNode(9998, 100, 'distributor', {9,})
  bc.startTransaction(9998, {1,})
  bc.changeParentNode(9998)
  bc.acceptTransactionRequest(9999)
  print(bc.accepted_transactions)
  print(manufacturer)
  print(bc.mineBlock())