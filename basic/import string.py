import string
name = input("enter nick")
while True:
          for l in name:
                    if l in string.ascii_letters or l in string.digits:
                              return(name) 
                              break

                    else:
                            break
                            
                              