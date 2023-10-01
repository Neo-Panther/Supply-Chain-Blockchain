# Blockchain Assignment 1

## Group Information (Name and ID)
1. Aryan Gupta: 2021A7PS0162H
2. Anmol Agarwal: 2021A7PS0136H
3. Ayush Nautiyal: 2021A7PS2607H
4. Mihir Kulkarni: 2021A7PS2689H
5. Aditya Aggarwal: 2021A7PS2380H

Here, we offer an overview of all the features implemented within the blockchain. The "main.py" file serves as the frontend for accessing these features, and their corresponding options are detailed alongside.

## main.py
Description of the functions used in "main.py"

### Registering New Nodes (Option 1)
manufacturer is added while creating the blockchain, all other nodes are added by calling the addNode function. Initial stake is calculated from their security deposit, id is calculated automatically (decreasing from 9999; 9999 alloted to the manufaturer). {id is sometimes referred to as address; because they are supposed to be derived from the real (network) address of the nodes in the network}

Each node is assigned a public and private key upon creation. Initial stock is optional. The node will start with empty if an initial stock is not specified. If initial stock is specified, it is saved in product_locations until used in a transaction.

The types a node can take are defined in NodeType Enum class. NodePublicInfo Data class gives a template for the public information of a node; available with all nodes (id, stake, stock, type, public key). 

### Change Simulated Node (Option 2)
Change the current node of the blockchain. This changes the perspective of the blockchain network to the node entered. Since it is not possible to change nodes actually, this is simulated by changing the parent node field of blockchain class; this removes the private data of the old node, like its private; and replaces it with the new one.

### Starting a Transaction (Option 3)
Any node in the blockchain can start a transaction unless it already has a pending or unverified transaction. A transaction in our implementation is started by the sender node addressed to the reciever node, complete with the product ids. A node can only send the product ids it has in stock. The sender node is blocked until the transaction is rejected by the reciever node, or it is verified in the next mining. The transaction is signed automatically by the sender node's private key, detected from the current node assigned in the blockchain.

**Note:** The current node is considered the sender of the transaction.

### Getting product status (Option 4) - QR Code
Using the input product id we search linearly through all the blocks of the blockchain to find the most recent transaction in which the product was used. If the product was not used in a transaction, we go through the stocks of all the products (stored as a product_location dictionary for convinience). The output is saved in a qr code locally, and also opened at the time of execution.

### Printing the Blockchain (Option 5)
All the blocks in the blockchain are printed from the latest to genesis block.

### Mining a Block (Option 6)
When a node calls the mining function; it starts the voting process, a new block is mined of there are valid transactions, as described below.

#### Consensus Algorithm
The DPoS Consensus Algorithm has been implemented in the voting function; defined inside the mineBlock function. 

Voting power of a node is calculated by adding its stake, stock and a random number between 0 and the maximum stake in the network. This allows all nodes to be validators and miners; but those nodes with a higher voting power have a much better chance to be chosen. 3 or more delegates are randomly chosen from the nodes; simulating the nodes which have started mining and have voted themselves. The remaining nodes vote for one among these delegates (simulated by random voting).

The delegates with the highest vote becomes the miner and two others are chosen as validators (Many more are chosen in a real network). A new block is added only if atleast 2 out of the three validate and confirm the block. On successful mining; validators, miners and those who voted for them are rewarded.

#### Validating a block:
Before validating a block; all accepted transactions in the network are verified (by miners and validators). These are then added to a temporary block and broadcasted to the network (simulated). The validators then validate the block by calling validateBlock.

  validateBlock recomputes the merkle tree, checks its previous hash, height, and recalculates its header hash.

  If the block is found to be invalid or if double spending is detected the responsible nodes are penalized.

#### Validating a Transaction
A transaction is validated by verifying the sender & reciever signatures using their public keys; and checking the stock of sender for the mentioned product ids. If double spending is detected the responsible nodes are penalized, an invalid transaction is dropped. After the  

### Printing information on the parent node (Option 7)
Returns the publically available data of this node, the stock set's reference is returned.

### Get information on pending transactions (Option 8)
The function returns the list pending transactions mapped to the current parent node.

### Confirm a Transaction Request (Option 9)
Given the id of the sender as argument the reciever accepts or rejects a transaction. If the reciever has already started or accepted a transaction, it is blocked and cannot accept any more.

### Reject a Transaction Request (Option 10)
Reject a transaction, the initiator is notified and removed from blocked_nodes

### End Connection with Blockchain (Option 11)
End the connection to the blockchain (exit the program)

### Add product to Blockchain (Manufacturer's stock) (Option 12)
Manufacturer makes a transaction to himself to intorduce new products into the blockchain. This is the only transaction to oneself allowed in the blockchain.

### Delete a Started Transaction (Option 13)
If the sender feels that the receiver is taking too long to respond; it may delete the transaction started by it. This allows the node to start a new transaction.

## Merkle Tree
we construct a merkle tree.
Each transaction is hashed using a cryptographic hash function (e.g., SHA-256). The hash of a transaction is a fixed-size string of characters that uniquely represents the transaction's content.

Any change in a transaction would lead to a change in its hash, which, in turn, would affect the Merkle Root. Therefore, if someone tries to tamper with a transaction within a block, it becomes evident because the Merkle Root in the block header would no longer match the recalculated Merkle Root.

Pair the transaction hashes in the list and we hash them together. If there's an odd number of transaction hashes, we duplicate the last hash to create an even number of pairs.We continue this process until we have only one hash remaining, which will be the Merkle Root.

## Well known issues
### A new transaction must only be started when the previous transactions are verified

**Solution**
A node can only start or accept a transaction if the previous transaction it has been involved in (if any) has been verified and completed. 
> Implemented using blocked_nodes field in the Blockchain class

### The distributor has dispatched the product, and the client has received it, but the client is denying it (The client is lying, but the distributor is not)

**Solution**
Until the client puts its signature on the transaction and it gets verified by atleast 2 validators; only then will the products be added to client's stock. The client's signature prevents it from lying.
> A Transaction's operations are carried out after verification (validateTransaction), its addition to a new block, and verification by two validators (simulated). All this is done in mineBlock.
*Note:* If the client somehow already has a product id; we merge both the product ids. Since it is not possible (without malicious usage) to use the same product id two times (because of how the blockchain is implemented); we penalize the client.

### The distributor has not dispatched the product, and the client has not received it (The client is not lying, but the distributor is)

**Solution**
If the dispatcher does not have the mentioned products, it will be found out during validation of the transaction (validateTransaction called in mineBlock) and the dispatcher will be penalized.

**Assumptions:**
1. Any Node can start a Transaction with any other
2. Client's signature proves that it has seen the products; but it will only be added to its stock (handed over to him) after validation. Client can start the voting process to expediate the same. Any node can start the voting process - by calling mineBlock method; but only the chosen miner can add block. It must also be verified by the chosen validators. (Responsibilty of checking if the dispatcher has sent the products falls with the client and the validators; Responsibility of checking if the client has received the products lies with the validators)
*Note:* The "main.py" file is the frontend endpoint of our code; its functions have been described in this file. Comments describing the core blockchain file have been placed in "blockchain.py"
