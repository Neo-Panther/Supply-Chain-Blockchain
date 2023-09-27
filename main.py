from blockchain import *

print("Creating Blockchain")
print("Enter initial products with manufacturer-")
stock = map(int, input("Enter space separated product-ids: ").split())
manufacturer = Node(100000000, 99999, stock, NodeType.MANUFACTURER)
bc = Blockchain(manufacturer)
print("Blockchain created")
while(True){
  print("Choose an operation to perform:")
  
}