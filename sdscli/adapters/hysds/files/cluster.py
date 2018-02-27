from sdscli.adapters.hysds.fabfile import *


#####################################
# add custom fabric functions below
#####################################

def test():
    """Test fabric function."""

    run('whoami')
