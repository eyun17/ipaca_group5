""" 
IPACA domain model

This implements a tree-structure

We deal with 2 different approaches: 
1) The main teses group will get a quite detailed tree without updating our beliefs
2) The passive voice group will just get 4 different difficulty levels. Here we will update our beliefs
"""
from learning_environment.models import Task


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


    # some function for updating a tree
    
    
