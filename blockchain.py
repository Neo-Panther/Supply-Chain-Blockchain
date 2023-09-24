from datetime import datetime
import hashlib
from typing import Dict, List

class Node():
  def __init__(self, address: str, stake: int, id: str):
    self.address = address
    self.stake = stake
    self.id = id

class Transaction():
  def __init__(self, manufacturer_id: int, product_id: int, client_id: int, distributor_id: int, amount: int):
    self.manufacturer_id = manufacturer_id
    self.product_id = product_id
    self.client_id = client_id
    self.distributor_id = distributor_id
    self.amount = amount
    self.timestamp = datetime.now()
    self.transaction_id = distributor_id^product_id^client_id
  
class Block():
  def __init__(self, prev_hash: str, height: int, transactions: List[Transaction]):
    self.previous_hash = prev_hash
    self.merkle_root = Blockchain.computeMerkleRoot(transactions)
    self.height = height
    self.timestamp = datetime.now()
    self.header_hash = Blockchain.calculateHash(prev_hash + self.merkle_root + height + self.timestamp.strftime("%d|%m|%Y><%H:%M:%S"))

class Blockchain():
  def __init__(self):
    self.blockchain: Dict[str, self.Block] = dict()
    self.nodes = set()
    self.nodes.add(Block(self.calculateHash(''), 0, []))
    self.unverified_transactions: List[Transaction] = []

  @staticmethod
  def computeMerkleRoot(transactions: List[Transaction]) -> str:
    items = transactions.copy()
    

  @staticmethod
  def calculateHash(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()
  
  def addBlock(self, ):
    pass