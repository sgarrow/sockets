'''
When a client enters a command those commands are received by function
handleClient in file server.py.  The command (string) is forwarded to
function "vector" (in this file) and the appropriate "worker" function
is then vectored to in file cmdWorkers.py.
'''

import cmdWorkers as cw
#############################################################################

def killSrvr(): # The ks handled directly in the handleClient func so it
    return      # doesn't need a wrk funct, but because of the way vectoring
                # is done a func needs to exist. This func never called/runs.
#############################################################################

def getVer():
    ver = ' v0.2.1 - 12-Jan-2024'
    return [ver]
#############################################################################

def vector(inputStr): # called from handleClient. inputStr from client.

    # This dictionary embodies the worker function vector (and menu) info.
    vectorDict = {
    'f0' : { 'func': cw.f0,    'parm': [1,2,3], 'menu': 'Function 0'  },
    'f1' : { 'func': cw.f1,    'parm': [4,5,6], 'menu': 'Function 1'  },
    'f2' : { 'func': cw.f2,    'parm': None,    'menu': 'Function 2'  },
    'gv' : { 'func': getVer,   'parm': None,    'menu': 'Get Version' },
    'ks' : { 'func': killSrvr, 'parm': None,    'menu': 'Kill Server' }
    }

    # Process the string (command) passed to this function via the call
    # from function handleClient in file server.py.
    inputWords = inputStr.split()

    if inputWords == []:       # In case user entered just spaces.
        rspStr = 'Invalid command'
        return rspStr          # Return to srvr for forwarding to clnt.

    choice     = inputWords[0]

    if choice in vectorDict:
        func   = vectorDict[choice]['func']
        params = vectorDict[choice]['parm']

        if params is None:
            rsp = func()       # rsp[0] = rspStr. Vector to worker.
            return rsp[0]      # return to srvr for forwarding to clnt.

        rsp = func(params)     # rsp[0] = rspStr. Vector to worker.
        return rsp[0]          # Return to srvr for forwarding to clnt.

    if choice == 'm':
        rspStr = ''
        for k,v in vectorDict.items():
            rspStr += ' {:2} - {}\n'.format(k, v['menu'] )
        return rspStr          # Return to srvr for forwarding to clnt.

    rspStr = 'Invalid command'
    return rspStr              # Return to srvr for forwarding to clnt.
