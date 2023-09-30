# Blockchain Assignment 1
## Registering New Nodes
manufacturer is added while creating the blockchain, all other nodes are added by calling the addNode function. Defined as:

> addNode(self, n_address: int, initial_stake: int, type: Literal['client', 'distributor'], n_stock: set[int] = set()) -> None:

Each node is assigned a public and private key upon creation. Initial stock is optional; and the node will start empty if an initial stock is not specified.

The types a node can take are defined in NodeType Enum class. NodePublicInfo Data class gives a template for the public information of a node; available with all nodes. 

## Consnensus Algorithm
The DPoS Consensus Algorithm has been implemented in the voting function; defined inside the mineBlock function. 

Voting power of a node is calculated by adding its stake, stock and a random number between 0 and the maximum stake in the network. This allows all nodes to be validators and miners; but those nodes with a higher voting power have a much better chance to be chosen. 3 or more delegates are randomly chosen from the nodes; simulating the nodes which have started mining and have voted themselves. The remaining nodes vote for one among these delegates (simulated by random voting).

The delegates with the highest vote becomes the miner and two others are chosen as validators (Many more are chosen in a real network). A new block is added only if atleast 2 out of the three validate and confirm the block. On successful mining; validators, miners and those who voted for them are rewarded.

### Validating a block:
Before validating a block; all accepted transactions in the network are verified (by miners and validators). These are then added to a temporary block and broadcasted to the network (simulated). The validators then validate the block by calling validateBlock.

  validateBlock recomputes the merkle tree, checks its previous hash, height, and recalculates its header hash.

  If the block is found to be invalid or if double spending is detected the responsible nodes are penalized.

## Anmol

## Printing information on the parent node
returns: publically available data of this node, the stock set's reference is returned, 
the following format is followed
 'id': self.id,
      'stake': self.stake,
      'stock': self.stock,
      'type': self.type,
      'public_key': self.public_key
## get information on pending transactions

the function returns the list pending transactions mapped to the current parent node 

def getPendingTransactions(self) -> list[str]:
    return [str(txn) for txn in self.pending_transactions[self.parent_node.id]]
## Confirm a Transaction Request
takes id of sender as the argument
The function first checks if older transactions are pending for the current node
Accept a transaction, the acceptor is added to the blocked_nodes list, transaction moved to accepted_transactions
  """
## Reject a Transaction Request 
Reject a transaction, the initiator is notified and removed from blocked_nodes

## End Connection with Blockchain
  
## Add product to Blockchain (Manufacturer's stock): 12

