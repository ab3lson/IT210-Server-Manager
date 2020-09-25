#!/usr/bin/python3

import argparse
import os
import sys
from resources import *

def main_menu():
  print("""
██████╗  ██╗ ██████╗     ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗ ███████╗
╚════██╗███║██╔═████╗    ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗██╔════╝
 █████╔╝╚██║██║██╔██║    ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝███████╗
██╔═══╝  ██║████╔╝██║    ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗╚════██║
███████╗ ██║╚██████╔╝    ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║███████║
╚══════╝ ╚═╝ ╚═════╝     ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝
Optional: Use with -h or --help for command line arguments


  """)
  exit()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(prog='210ServerManager.py', description="IT 210 Live Server Management Tool.", add_help=False)
  create = parser.add_argument_group("Create Live Servers (Optional)").add_mutually_exclusive_group()
  delete = parser.add_argument_group("Delete Live Servers (Optional)").add_mutually_exclusive_group()
  admin = parser.add_argument_group("Live Servers Admin Tools (Optional)").add_mutually_exclusive_group()

  create.add_argument('-c','--create', type=str, action='store', metavar='PATH', nargs=1, help='creates a live server for each student in the class from a csv')
  create.add_argument('-co', '--create-one', action='store', metavar='NETID', nargs=1, type=str, help='creates a live server for one student')
  delete.add_argument('-d','--delete', nargs='?', const='no_args', metavar='RANGE', help='deletes a given range of live servers')
  delete.add_argument('-do','--delete-one', type=str, action='store', metavar='NETID', nargs=1, help='deletes a live server for one student')
  admin.add_argument('-e','--enter', type=str, action='store', metavar='NETID', nargs=1, help='enter a student\'s live server')
  admin.add_argument('-l','--list', type=str, action='store', metavar='NETID', nargs='?', const='all_students', help='display a list of paired NetIDs and VM IDs')


  parser.add_argument('-h','--help', action='help', help='show this help message and exit')

  args = parser.parse_args()

  if len(sys.argv) < 2:
    main_menu()

  if args.create:
    create_live_servers.create_multiple(args.create[0])
  elif args.create_one:
    create_live_servers.create_one(args.create_one[0])
  elif args.delete == [] or args.delete:  #no argument is possible
    delete_live_servers.delete_multiple()
  elif args.delete_one:
    delete_live_servers.delete_one(args.delete_one[0])
  elif args.enter:
    print("-e was selected")
    print("The NetID is:", args.enter[0])
  elif args.list == [] or args.list:  #no argument is required
    admin_tools.list(args.list)  #passes NetID if provided
  else:
    raise Exception("Invalid arguments were chosen.")
    exit()
    
  
  
