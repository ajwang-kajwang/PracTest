#
# characters.py - classes to represent students and training
#
# Student Name : Ima Student
# Student ID   : 12345678
#
import random

def get_namelist(slist):
    """ extracts the names from a list of Student objects
    
    Parameters
    ----------
    slist : list
        The list of students

    Returns
    -------
    newlist : list  
        The list of student names (strings)  
    """
    
    newlist = []
    for s in slist:
        newlist.append(s.get_name())
    return newlist

def get_ranklist(slist, c_ref):
    """ extracts rank colours and indexes from a list of Student objects
    
    Parameters
    ----------
    slist : list
        The list of students

    c_ref : list
        List of ordered rank colours to get rank numbers 

    Returns
    -------
    rc_list : list  
        The list of student rank colours (strings) in order 

    rn_list : list  
        The list of student rank numbers (integers) in order 
    """
    
    rc_list = []
    for s in slist:
        rc_list.append(s.get_rank())
    rn_list = [c_ref.index(n) for n in rc_list]
    return rc_list, rn_list

class Student():
    """
    A class used to represent a Student

    Attributes
    ----------
    name : str
        the name of the student
    pos : tuple 
        (x,y) position of the student
    rank : string
        the rank of the student - a string with a colour representing rank

    Methods
    -------
    __init__(name, pos, rank)
        initialises the student with name, position and rank (colour)
    __str__()
        returns key object information as a string
    get_pos()
        returns the position tuple
    get_rank()
        returns the string holding the rank
    get_name()
        returns the name of the Student
    set_pos(pos)
        updates the position of the Student, pos is (x,y) tuple
    step_change(set_move=None)
        calculates random Moore movement, OR takes outside movement in set_move
    """

    def __init__(self, name, pos, rank):
        """initialises the student with name, position and rank (colour)"""
        self.name = name
        self.pos = pos
        self.rank = rank

    def __str__(self):
        """returns key object information as a string"""
        return(self.name)

    def get_pos(self):
        """returns the position tuple"""
        return self.pos

    def get_rank(self):
        """returns the string holding the rank"""
        return self.rank

    def get_name(self):
        """returns the name of the Student"""
        return self.name

    def set_pos(self, pos):
        """updates the position of the Student, pos is (x,y) tuple"""
        self.pos = pos

    def step_change(self, set_move=None):
        """defines movements for student on each step - Moore neighbourhood"""
        if not set_move:
            pos_x = self.pos[0]
            pos_y = self.pos[1]
            move_x = random.randint(-1,1)
            move_y = random.randint(-1,1)
            pos_x = pos_x + move_x
            pos_y = pos_y + move_y
            self.pos = (pos_x, pos_y)
