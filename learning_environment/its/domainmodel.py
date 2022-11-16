""" 
IPACA domain model

This implements a tree-structure

We deal with 2 different approaches: 
1) The main teses group will get a quite detailed tree without updating our beliefs
2) The passive voice group will just get 4 different difficulty levels. Here we will update our beliefs
"""
from learning_environment.models import Task
import math


class TaskTree:
    """
    Just a normal Tree :)
    """
    def __init__(self, parent = None, children:list = [], data = None):
        self.parent = parent,
        self.children = children,
        self.data = data
        

    # the getter:
    def get_children(self):
        return self.children

    def get_parent(self):
        return self.parent
    
    def get_data(self):
        return self.data
    
    # the setter:
    def set_children(self, children):
        self.children = children
    
    def set_parent(self, parent):
        self.parent = parent
    
    def set_data(self, data):
        self.data = data
    
    # additional functions
    def is_root(self):
        return self.parent == None

    def is_leaf(self):
        return self.children == []

    def add_child(self, child):         # adds child to existing list of children
        return self.children.append(child)
    
    def remove_child(self, child):      # removes existing child from list of children
        if child in self.children:
            self.children.remove(child)
        else:
            raise ValueError("remove_child: child not found")


class Domainmodel:
    """
    Our domain model
    """
    def __init__(self, tree:TaskTree = None):
        self.tree = tree
    
    # some funtion for building a tree
    def build_tree(self, tasklist:list = []):
        root = TaskTree(data = "root")

        # set difficulty levels as children
        for i in range(4):
            root.add_child(TaskTree(parent=root, data=i))
        
        # divide tasklist equaly
        len = len(tasklist)
        quater = len/4
        ceil = math.ceil(quater)
        floor = math.floor(quater)


        if len % 4 == 0:
            divider = [quater, quater*2, quater*3, quater*4]

        if len % 4 == 1:
            # 1. len%4 == 1  -> 1x ceil, 3x floor
            divider = [ceil, ceil + floor, ceil + 2*floor, ceil + 3*floor]

        if len % 4 == 2:
            # 2. len%4 == 2  -> 2x ceil, 2x floor
            divider = [ceil, 2*ceil, 2*ceil + floor, 2*ceil + 2*floor]

        if len % 4 == 3:
            # 3. len%4 == 3  -> 3x ceil, 1x floor
            divider = [ceil, 2*ceil, 3*ceil, 3*ceil + floor]
        
        #for div in range(4):
            # root get children, data == div, set child with data = tasklist[divider[div]:divider[div+1]]

 
    def build_tree(self, dict:dict = None):
        return None         #TODO: build a tree from dict

    # some function for updating a tree    
    def update_tree(self, task, difficulty):
        return None        # TODO: update tree