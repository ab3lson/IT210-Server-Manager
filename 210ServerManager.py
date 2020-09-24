#!/usr/bin/python3

import argparse
import os
import sys
from resources import create_live_servers

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
  delete.add_argument('-d','--delete', type=str, action='store', metavar='NETID',  nargs=1, help='deletes all student\'s live servers')
  delete.add_argument('-do','--delete-one', type=str, action='store', metavar='NETID', nargs=1, help='deletes a live server for one student')
  admin.add_argument('-e','--enter', type=str, action='store', metavar='NETID', nargs=1, help='enter a student\'s live server')
  
  parser.add_argument('-h','--help', action='help', help='show this help message and exit')

  args = parser.parse_args()

  if len(sys.argv) < 2:
    main_menu()

  print("ARGS:",args)
  if args.create:
    print("-c was selected")
    print("The filepath is:", args.create[0])
    create_live_servers.create_multiple(args.create[0])
  elif args.create_one:
    print("-co was selected")
    print("The NetID is:", args.create_one[0])
    create_live_servers.create_one(args.create_one[0])
  elif args.delete:
    print("-d was selected")
    print("The NetID is:", args.delete[0])
  elif args.delete_one:
    print("-do was selected")
    print("The NetID is:", args.delete_one[0])
  elif args.enter:
    print("-e was selected")
    print("The NetID is:", args.enter[0])
  else:
    raise Exception("Invalid arguments were chosen.")
    exit()
    
  
  
