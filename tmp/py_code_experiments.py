code = """
def B():                    # qualname: B
         print("start B")
         def bb():                  # qualname: B.<locals>.bb
             b = 10 #WATCH_AFTER: b
             return "test __qualname__"
             
         print( bb(), bb.__qualname__ )
         
         x = 42 #WATCH_AFTER: x; x-10  
         u = (A(
           x=C() ,
           y=3,
            z=2
              
         )
         )
   """
import py
s = py.code.Source( code )
print( s.getstatement(12) )
