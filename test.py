# Importing library
import qrcode

# Data to be encoded
if __name__ == '__main__':
  data = 'QR Code using make() function'
  img = qrcode.make(data)
  print('')
  img.save('MyQRCode1.png')
