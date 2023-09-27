from blockchain import *

print("Creating Blockchain")
print("Enter initial products with manufacturer-")
stock = map(int, input("Enter space separated product-ids: ").split())
manufacturer = Node(100000000, 99999, stock, NodeType.MANUFACTURER)
bc = Blockchain(manufacturer)
print("Blockchain created")
while(True):

  print("Menu: \n")
  print("To Add Node: 1 \n")
  print("To make Transaction: 2 \n")
  print("To change Node: 3 \n")
  print("Get Product Status: 4 \n")
  print("Display blockchain: 5 \n")
  print("mine block : 6 \n")

  s=input("chooose an operation to perform ")
  
  if s==1:
    print()
