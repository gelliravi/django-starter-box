import cssmin as cssmin_mod
import slimit as slimit_mod

def cssmin(content):
    """
    :type   content: str  
    """

    return cssmin_mod.cssmin(content)
 
def csspath(content):
    """
    :type   content: str  
    """
    
    # TODO
    return content 

def slimit(content):
    """
    :type   content: str  
    """
    
    return slimit_mod.minify(content, mangle=True, mangle_toplevel=False)
    
