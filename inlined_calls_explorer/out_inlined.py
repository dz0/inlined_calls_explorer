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
                  #@inline 3: code_simple. C.[locals].generator_ 
                  def generator_():
                      genexpr_ = (x for x in [5, 6, 7])
                      for a in genexpr_:
                         yield a #WATCH: a; a*2
#WATCH: a 5
#WATCH: a*2 10
                  #@return: generator_ => 5
                  #@inline 3: code_simple. C.[locals].generator_ 
                  def generator_():
#WATCH: a 6
#WATCH: a*2 12
                  #@return: generator_ => 6
                  #@inline 3: code_simple. C.[locals].generator_ 
                  def generator_():
#WATCH: a 7
#WATCH: a*2 14
                  #@return: generator_ => 7
                  #@inline 3: code_simple. C.[locals].generator_ 
                  def generator_():
DBG WEIRD EVENT exception <code object generator_ at 0x7fa36e20fb70, file "../tests/code_simple.py", line 38>
                  #@return: generator_ => None
                  lambda_ = lambda x: x*x
                  mapped = map(lambda_, listcomp_) 
                  list(mapped)  # to activate lazy mapping
                  return 2
         #@return: C => 2
           y=3,
            z=2
         #@inline 2: code_simple. A 
         def A(*args, **kwargs):
              a = 5
              print(
                "A"
A
              if a > 10:  #WATCH: a
#WATCH: a 5
                  print("a <= 10")
a <= 10
              c = C()  #WATCH_AFTER: c
              #@inline 3: code_simple. C 
              def C():
C
              #@inline 4: code_simple. C.[locals].generator_ 
              def generator_():
#WATCH: a 5
#WATCH: a*2 10
              #@return: generator_ => 5
              #@inline 4: code_simple. C.[locals].generator_ 
              def generator_():
#WATCH: a 6
#WATCH: a*2 12
              #@return: generator_ => 6
              #@inline 4: code_simple. C.[locals].generator_ 
              def generator_():
#WATCH: a 7
#WATCH: a*2 14
              #@return: generator_ => 7
              #@inline 4: code_simple. C.[locals].generator_ 
              def generator_():
DBG WEIRD EVENT exception <code object generator_ at 0x7fa36e20fb70, file "../tests/code_simple.py", line 38>
              #@return: generator_ => None
              #@return: C => 2
              for x in range(3):
#WATCH: c 2
                  C()
                  #@inline 3: code_simple. C 
                  def C():
C
                  #@inline 4: code_simple. C.[locals].generator_ 
                  def generator_():
#WATCH: a 5
#WATCH: a*2 10
                  #@return: generator_ => 5
                  #@inline 4: code_simple. C.[locals].generator_ 
                  def generator_():
#WATCH: a 6
#WATCH: a*2 12
                  #@return: generator_ => 6
                  #@inline 4: code_simple. C.[locals].generator_ 
                  def generator_():
#WATCH: a 7
#WATCH: a*2 14
                  #@return: generator_ => 7
                  #@inline 4: code_simple. C.[locals].generator_ 
                  def generator_():
DBG WEIRD EVENT exception <code object generator_ at 0x7fa36e20fb70, file "../tests/code_simple.py", line 38>
                  #@return: generator_ => None
                  #@return: C => 2
                  #@inline 3: code_simple. C 
                  def C():
C
                  #@inline 4: code_simple. C.[locals].generator_ 
                  def generator_():
#WATCH: a 5
#WATCH: a*2 10
                  #@return: generator_ => 5
                  #@inline 4: code_simple. C.[locals].generator_ 
                  def generator_():
#WATCH: a 6
#WATCH: a*2 12
                  #@return: generator_ => 6
                  #@inline 4: code_simple. C.[locals].generator_ 
                  def generator_():
#WATCH: a 7
#WATCH: a*2 14
                  #@return: generator_ => 7
                  #@inline 4: code_simple. C.[locals].generator_ 
                  def generator_():
DBG WEIRD EVENT exception <code object generator_ at 0x7fa36e20fb70, file "../tests/code_simple.py", line 38>
                  #@return: generator_ => None
                  #@return: C => 2
                  #@inline 3: code_simple. C 
                  def C():
C
                  #@inline 4: code_simple. C.[locals].generator_ 
                  def generator_():
#WATCH: a 5
#WATCH: a*2 10
                  #@return: generator_ => 5
                  #@inline 4: code_simple. C.[locals].generator_ 
                  def generator_():
#WATCH: a 6
#WATCH: a*2 12
                  #@return: generator_ => 6
                  #@inline 4: code_simple. C.[locals].generator_ 
                  def generator_():
#WATCH: a 7
#WATCH: a*2 14
                  #@return: generator_ => 7
                  #@inline 4: code_simple. C.[locals].generator_ 
                  def generator_():
DBG WEIRD EVENT exception <code object generator_ at 0x7fa36e20fb70, file "../tests/code_simple.py", line 38>
                  #@return: generator_ => None
                  #@return: C => 2
              return a
         #@return: A => 5
         print("end B")
end B
#@return: B => None
