#
# characters.py - classes to represent students and training
#
# Student Name : Ima Student
# Student ID   : 12345678
#
class Student():
    
    def __init__(self, name, pos, rank):
        self.name = name
        self.pos = pos
        self.rank = rank

    def __str__(self):
        return(self.name)

    def get_pos(self):
        return self.pos

    def get_rank(self):
        return self.rank

    def get_name(self):
        return self.name

    def set_pos(self, pos):
        self.pos = pos
