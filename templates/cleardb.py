#!/usr/bin/python
# Filename: cleardb.py
# Description: Clears all tables in an SQLite database

import sys, os, sqlite3

def get_app_info():
	return {
		"executable": "cleardb.py",
		"name"		: "Database Cleaner",
		"version"	: "Version: 1.0 [07 Mar 2017]",
		"usage"		:[ 	"[-h][-?] file"
					],
					
		"args"		:[
			    ["h"	, ["Print help.", usage]],
			    ["?"	, ["Print help.", usage]],
			    ["file"	, ["Database file or directory.", None]]
				]		
		}
	


def usage(nCmd):
	Format	= "name,version,copyright,website"
	AppInfo	= get_app_info()
	
	# Print header
	for attr in Format.split(','):
		if AppInfo.get(attr):
			print( AppInfo[attr] )

	# Print usage			
	print("\nUsage:\n    {}\t{}\n\nOptions:".format(
					AppInfo['executable'], 
					"\n\t\t".join(AppInfo["usage"])) )

	# Pring argument description			
	for help in AppInfo["args"]:
		if len(help[0]) < 3:
			indent	= '\t\t'
		else:
			indent	= '\t'
		
		print( "    -{}{}{}".format(help[0], indent, help[1][0]) )
	
	sys.exit(0)		    
	return

	
def GetTablesForConnection(conn):
	""" Returns the tables in a database 		
	Arguments
		conn -- Connection
	"""
	c		= conn.cursor()
	c.execute('SELECT name FROM sqlite_master WHERE type=\'table\''  )
	
	tables	= []
	for row in c:
		table	= row[0]
		
		# Skip internal sqlite tables
		if table.find('sqlite_') == 0:
			continue
	
		tables.append( table )
		
	c.close()
	return tables

def ClearDatabase(path):
	print( 'Processing database: {}.'.format(path) )
	conn	= sqlite3.connect(path)		
	
	# Get the list of tables
	tables	= GetTablesForConnection(conn)

	# Clear all the database
	for t in tables:
		# Skip type information tables
		if t.find('TYPE_') == 0:
			continue
			
		query	= 'DELETE FROM {}'.format(t)
		c	= conn.cursor()
		c.execute(query)
		
	conn.commit()
	
	# Compact the database
	c	= conn.cursor()
	c.execute('VACUUM')
	
	# Commit all changes
	conn.commit()
		
	c.close()
	return

def ProcessDirectory(directory):
	for root, dirs, files in os.walk(directory, topdown=False):
		for file in files:
			if file.find('.s3db') == -1:
				continue
			
			# Build the file path	
			path	= '{}{}{}'.format(root,os.sep,file)
			
			# Clear the database
			ClearDatabase(path)
	return
		
def execute():
	path	= sys.argv[-1]
	
	if os.path.isdir(path):
		ProcessDirectory(path)
	elif os.path.isfile(path):
		ClearDatabase(path)
	else:
		print( "Invalid directory or file." )
		
	return
	
def main():
	"""TODO:
	"""
	ArgNum	= len(sys.argv)
	
	if( ArgNum == 1 ):
		usage(0)
		return
		
	for n in range(1,ArgNum):
		arg	= sys.argv[n]
		if arg[0] != '-':
			continue
		
		AppInfo	= get_app_info()
		for arginfo in AppInfo["args"]:
			if arginfo[0] == arg[1:]:
				arginfo[1][1](n)
		
	execute()	
	return
	
if __name__ == "__main__":
    main()	

