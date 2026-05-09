

# a is only aviable in x's scope 
# def x():
#     let a = 1
# end 
#

# returns 2 
# a = 1
# def x():
#     a = a + 1 
#     return a
# end 
#

# if use a let keyword, will create'

# still unsure, can you do let a = 1 let a = 2 and it works?
class Scope:

    def __init__(self, parent=None):
        self.parent: Scope | None = parent
        self.table: dict = {}

    def get(self, key):
        if key in self.table:
            return self.table[key]
        if self.parent:
            return self.parent.get(key)
        else:
            return None
        
    def update():
        pass