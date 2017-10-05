if True:
   def A(*args, **kwargs): 
        a = 5
        print(
          "A"
          )
        if a > 10:  #WATCH: a
            print("a > 10")
        else:
            print("a <= 10")
        
        c = C()  #WATCH_AFTER: c
        for x in range(3):
            C()
        
        # D()
        return a
    

def B(): 
         print("start B")
         
         x = 42 #WATCH_AFTER: x; x-10  

         def bb():
             b = 10 #WATCH: b
             return "test __qualname__"
            
         print( bb(), bb.__qualname__ )
         bqn = bb() #WATCH_AFTER: bqn

         # D()
         # D()

         A()
         A()
         
         z= A(4, D(),      3)
         u = A(
           x=C() ,
           y=3,
            z=2
              
         )
         
        
         print("end B")

def C():
         print("C")
         def generator_():
             genexpr_ = (x for x in [5, 6, 7])
             for a in genexpr_:
                yield a #WATCH: a; a*2

         listcomp_ = [ x for x in generator_()  ]
         lambda_ = lambda x: x*x
         
         mapped = map(lambda_, listcomp_) 
         list(mapped)  # to activate lazy mapping
         return 2

def D():
    def dd():
        print("dd")
    # print("D")
    dd()
    return "D"

if __name__ == "__main__":
    # B()
    import test_simple
