#@inline 1: code_simple. B 
def B():
         def bb():
         print( bb(), bb.__qualname__ )
         #@inline 2: code_simple. B.[locals].bb 
         def bb():
             b = 10 #WATCH_AFTER: b
             return "test __qualname__"
#WATCH: b 10
         #@return: bb => test __qualname__
test __qualname__ B.<locals>.bb
         print("start B")
start B
         x = 42 #WATCH_AFTER: x; x-10  
         u = (A(
#WATCH: x 42
#WATCH: x-10 32
           x=C() ,
         #@inline 2: code_simple. C 
         def C():
                  print("C")
C
                  def generator_():
                  listcomp_ = [ x for x in generator_()  ]
                  #@inline 3: code_simple. C.[locals].[listcomp] 
                  def generator_():
                  listcomp_ = [ x for x in generator_()  ]
                  #@inline 4: code_simple. C.[locals].generator_ 
                  def generator_():
                      genexpr_ = (x for x in [5, 6, 7])
                      for a in genexpr_:
A
a <= 10
C
C
C
C
end B
