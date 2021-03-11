

def sig4(value):
   disp = str(value)[0:4]
   disp = "    " + disp
   disp = disp[-4:]
   return disp

z = 3.14159
print(sig4(z))

z = 3.1415
print(sig4(z))

z = 3.14
print(sig4(z))

z = 3.1
print(sig4(z))

z = 31
print(sig4(z))

z = 3
print(sig4(z))

z = 31.4159
print(sig4(z))

z = 314.15
print(sig4(z))

