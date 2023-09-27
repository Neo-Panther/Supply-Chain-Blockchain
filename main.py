from blockchain import *
from random import randint
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
  address:int=1000  
  s=input("chooose an operation to perform ")
 
  if s==1:
   a:str=input('enter input')
   stock = map(int, input("Enter space separated product-ids: ").split())
   bc.addNode(address,address*2,a,stock)
   address-=1
 
  elif s==2:
    a:int=input('enter node')
    bc.changeParentNode(a)

  elif s==3:
    if bc.parent_node.type=='distributor':
        a:int =input("enter name of client")
        b:int =input("enter product id")
        bc.startTransaction(a,b)

    if bc.parent_node.type=='manufacturer':
        a:int =input("enter name of distributor")
        b:int =input("enter product id") 
        bc.startTransaction(a,b)

  elif s==4:
     print(bc.pending_transactions)

  elif s==5:
     bc.mineBlock()

  elif s==6:
     bc.parent_node.getInfo()      
     
  elif s==7:
    a:int=input("enter product id")
    bc.getProductStatus(a)    





    
