import time
from blockchain import *
import cv2

# TODO: pprint nodes-transac requests, termcolor-color menu, dynamic wait time
def getInt(prompt: str) -> int:
  while(True):
    try:
      i = int(input(prompt))
      break
    except ValueError:
      print("Input not an integer, please enter again")
  return i

def getIntArr(prompt: str) -> list[int]:
  while(True):
    try:
      inp = map(int, input(prompt).split())
      break
    except ValueError:
      print("Input not a space-separeated integer array, please enter again")
  return list(inp)

print("Creating Blockchain")
print("Enter initial products with manufacturer::")
stock = set(getIntArr("Enter space separated product-ids (repeated ids will be considered only once): "))
manufacturer = Node(100000000, 9999, stock, NodeType.MANUFACTURER)
print("Manufacturer Node successfully created")
print("Node public info broadcasted to all nodes: ", manufacturer.getInfo())
bc = Blockchain(manufacturer)
print("Blockchain Created")
address = 9998
while(True):
  print("\n::::::::Option Menu::::::::")
  print("To Add Node: 1")
  print("Change Current Node: 2")
  print("Make a Transaction: 3")
  print("Get Product Status: 4")
  print("Display blockchain: 5")
  print("Mine Block: 6")
  print("Display Info of Nodes, Available with Current Node: 7")
  print("Display Transaction Requests: 8")
  print("Confirm a Transaction Request (Need to accept to receive the products): 9")
  print("Reject a Transaction Request (Product will be returned to sender): 10")
  print("End Connection with Blockchain: 11")
  if bc.parent_node.id == bc.manufacturer_id:
    print("Add product to Blockchain (Manufacturer's stock): 12")
  selection = getInt("Chooose an Operation to Perform: ")
 
  if   selection == 1:
    n_type = input('Enter Node Type (distributor or client): ')
    while n_type not in ('client', 'distributor'):
      print("Invalid Node Type, please enter again")
      n_type = input('Enter Node Type (distributor or client): ')
    stock = set(getIntArr("Enter Space Separated Unique Product-ids (leave blank to start with empty stock; repeated ids will be considered only once): "))
    inuse = stock.intersection(product_locations.keys())
    while inuse:
      print("Product ids", inuse, "already in use, please enter unique ids")
      stock = set(getIntArr("Enter Space Separated unique Product-ids (leave blank to start with empty stock; repeated ids will be considered only once): "))
      inuse = stock.intersection(product_locations.keys())
    
    stake = getInt("Enter Initial Security Deposit Value: ")

    bc.addNode(address, stake, n_type, stock)
    print("Node successfully created")
    print("Node public info broadcasted to all nodes: ", current_active_nodes[address].getInfo())
    address -= 1
 
  elif selection == 2:
    id = getInt("Enter the Node id to Change to (Enter 0 or an Invalid id to Stop): ")
    if id not in current_active_nodes:
      print("id not Found on the Network, Stopping")
      continue
    bc.changeParentNode(id)

  elif selection == 3:
    receiver_id = getInt("Enter the Receiver's id: ")
    if receiver_id not in current_active_nodes:
      print("id not Found on the Network, Stopping")
      continue
    print("Your current stock:", bc.parent_node.stock)
    product_ids = set(getIntArr("Enter Space Separated Product-ids to send, enter nothing or invalid id to stop (repeated ids will be considered only once): "))
    if not product_ids: continue
    if product_ids.difference(bc.parent_node.stock):
      print("Products not in Stock, Stopping")
      continue
    bc.startTransaction(receiver_id, product_ids)
    print("Transaction started, wait for response from receiver and next mining to complete this transaction")

  elif selection == 4:
    product_id = getInt("Enter the product id: ")
    file_name = bc.getProductStatus(product_id)
    print("Press any key to close qr code window and continue execution::")
    # Read qr_code
    img = cv2.imread(file_name)
    
    # Output qr code with window name as 'Product_Status'
    cv2.imshow('Product ' + str(product_id) + ' Status', img)
    
    # Maintain output window until
    # user presses a key
    cv2.waitKey(0)       
    
    # Destroying present windows on screen
    cv2.destroyAllWindows()
    print("Product status saved as qr in file: ", file_name)

  elif selection == 5:
    bc.showBlockchain()

  elif selection == 6:
    bc.mineBlock()

  elif selection == 7:
    print("Parent Node Info (with private key)::")
    print(bc.parent_node)
    print("Other Nodes' data available with parent (id, info)::")
    print([(i[0], i[1]) for i in bc.nodes.items()])

  elif selection == 8:
    print(bc.getPendingTransactions())
  
  elif selection == 9:
    sender_id = getInt("Enter the id of the sender of the transaction: ")
    bc.acceptTransactionRequest(sender_id)
  
  elif selection == 10:
    sender_id = getInt("Enter the id of the sender of the transaction: ")
    bc.rejectTransactionRequest(sender_id)

  elif selection == 11:
    print("Closing connection to the Blockchain Network...")
    break

  elif selection == 12 and bc.parent_node.id == bc.manufacturer_id:
    print("Products currently in the blockchain:", product_locations.keys())
    stock = set(getIntArr("Enter Space Separated Unique Product-ids (leave blank to start with empty stock; repeated ids will be considered only once): "))

    product_ids = set(getIntArr("Enter Space Separated Unique Product-ids, enter nothing or used id to stop (repeated ids will be considered only once): "))
    if not product_ids: continue
    if product_ids.intersection(product_locations.keys()):
      print("Products not in Stock, Stopping")
      continue
    bc.startTransaction(bc.manufacturer_id, product_ids)
    print("Transaction started, wait for next mining to add these products")
  
  for i in range(3, -1, -1):
    time.sleep(1)
    print("Moving ahead in", i, end = '\r')
  print()
