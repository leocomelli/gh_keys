class AnsibleFake(object):	
  params = None

  def __init__(self, params):
    self.params = dict({ 
   			  'action' : None,
    		  'user'   : None,
    		  'passwd' : None,
    		  'title'  : None,
    		  'key'    : None,
    		  'key_id' : None
    	     }, **params)