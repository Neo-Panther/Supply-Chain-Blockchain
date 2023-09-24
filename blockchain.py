from datetime import datetime
import hashlib
from typing import Any, Dict, List, Optional

class Node():
  def __init__(self, address: str, stake: int, id : str, stock: Dict[str, int]):
    self.address = address
    self.stake = stake
    self.id = id
    self.stock = stock
    self.

class Transaction():
  def __init__(self, manufacturer_id: int, product_id: int, client_id: int, distributor_id: int, amount: int):
    self.manufacturer_id = manufacturer_id
    self.product_id = product_id
    self.client_id = client_id
    self.distributor_id = distributor_id
    self.amount = amount
    self.timestamp = datetime.now()
    self.transaction_id = distributor_id^product_id^client_id
  
     def  __str__(self):
        return str(self.__dict__)
  
class Block():
  def __init__(self, prev_hash: str, height: int, transactions: List[Transaction]) -> None:
    self.previous_hash = prev_hash
    merkle_tree = MerkleTree(transactions)
    self.merkle_root = merkle_tree.getRootHash()
    self.height = height
    self.timestamp = datetime.now()
    self.header_hash = Blockchain.calculateHash(prev_hash + self.merkle_root + str(height) + self.timestamp.strftime("%d|%m|%Y><%H:%M:%S"))

class Blockchain():
  def __init__(self):
    self.blockchain: Dict[str, Block] = dict()
    self.nodes = set()
    genesis_block = Block(self.calculateHash(''), 0, [])
    self.blockchain[genesis_block.header_hash] = genesis_block
    self.unverified_transactions: List[Transaction] = []
    self.newest_block = genesis_block.header_hash
  
  @staticmethod
  def calculateHash(s: Any) -> str:
    return hashlib.sha256(str(s).encode()).hexdigest()
  
  def addBlock(self,prev_hash:str):
        timeStamp=datetime.now()
        

class MerkleNode():
    def __init__(self, value: str, left = None, right = None) -> None:
      self.left: Optional[MerkleNode] = left
      self.right: Optional[MerkleNode] = right
      self.value = value
    
class MerkleTree():
  def __init__(self, transactions: List[Transaction]) -> None:
    self.tree_root: MerkleNode = self.__buildTree([MerkleNode(Blockchain.calculateHash(txn)) for txn in transactions])

  def __buildTree(self, transactions: List[MerkleNode]) -> MerkleNode:
    if len(transactions) == 1: 
      return transactions[0]
    else:
      next_level: List[MerkleNode] = []
      if len(transactions) % 2:
        transactions.append(transactions[-1])
      while transactions:
        left = transactions.pop()
        right = transactions.pop()
        next_level.append(MerkleNode(Blockchain.calculateHash(left.value+right.value), left, right))
      return self.__buildTree(next_level)

  def getRootHash(self) -> str:
    return self.tree_root.value