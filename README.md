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

## merkle tree
we construct a merkle tree.
Each transaction is hashed using a cryptographic hash function (e.g., SHA-256). The hash of a transaction is a fixed-size string of characters that uniquely represents the transaction's content.

Any change in a transaction would lead to a change in its hash, which, in turn, would affect the Merkle Root. Therefore, if someone tries to tamper with a transaction within a block, it becomes evident because the Merkle Root in the block header would no longer match the recalculated Merkle Root.

Pair the transaction hashes in the list and we hash them together. If there's an odd number of transaction hashes, we duplicate the last hash to create an even number of pairs.We continue this process until we have only one hash remaining, which will be the Merkle Root.

## Well known issues
### A sender can initiate a transaction when his/hers previous transactions are verified.

### solution

All nodes whose previous transactions are pending are added into blocked, if there id is in the list of blocked nodes they cant initiate a transaction.

### The distributor has dispatched the product, and the client has received it, but the client is denying it  
 Until the client puts signature on transaction,it is pending and client will not receive it.Eventually the product will be returned and transaction would be rejected.

### The distributor has not dispatched the product, and the client has notreceived it (The client is not lying, but the distributor is)
If he does not have the product, he will be penalized for double spending.
On the other hand if he doesnt dispatch it,the client will eventually cancelit