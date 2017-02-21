# this is the base class for visiting nodes in the Abstract Syntax Tree
# the Interpreter class extends this

class NodeVisitor(object):

    # when visit is called, call the visit_(nodetype) fuction
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    #this shouldn't happen, uh-oh!
    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))
