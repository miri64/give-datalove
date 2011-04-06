#!/usr/bin/env python
import sys,config
import web
import db_handling as dbh

web.config.debug = False

if __name__ == '__main__': 
    if len(sys.argv) != 2:
        sys.stderr.write("""Usage: %s <amount>
        
<amount>\tInteger number, that is the number of datalove points 
\t\tthat should be given to all users.

""" % sys.argv[0])
        exit(1)
    amount = int(sys.argv[1])
    db = web.database(
       	    dbn=config.db_engine, 
            db=config.db_name, 
            user=config.db_username, 
            pw=config.db_password
        )
    
    db_handler = dbh.DBHandler(db)
    
    db_handler.spread_free_datalove(amount)
