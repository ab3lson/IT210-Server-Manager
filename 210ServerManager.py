#!/usr/bin/python3

import argparse
import os
import sys
from resources import *

class color:
  PURPLE = '\033[95m'
  BLUE = '\033[94m'
  GREEN = '\033[92m'
  YELLOW = '\033[93m'
  RED = '\033[91m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  RESET = '\033[00m'

def main_menu(menu_options):
  print("""
██████╗  ██╗ ██████╗     ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗ ███████╗
╚════██╗███║██╔═████╗    ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗██╔════╝
 █████╔╝╚██║██║██╔██║    ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝███████╗
██╔═══╝  ██║████╔╝██║    ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗╚════██║
███████╗ ██║╚██████╔╝    ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║███████║
╚══════╝ ╚═╝ ╚═════╝     ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝
Web GUI: https://192.168.10.41:8006/
Optional: Use with -h or --help for command line arguments
  """)

  for i, option in enumerate(menu_options):
    if i %2 == 0: print("")
    print(f"{color.BLUE}[{i + 1}]{color.RESET} {menu_options[i]}", end='\t')
  print("\n")


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
  admin.add_argument('-m','--move', type=str, action='store', metavar='NETID', nargs=1, help='move a live server to a different IP')
  admin.add_argument('-l','--list', type=str, action='store', metavar='NETID', nargs='?', const='all_students', help='display a list of paired NetIDs and VM IDs')

  parser.add_argument('-h','--help', action='help', help='show this help message and exit')
  args = parser.parse_args()

  if args.create:
    create_live_servers.create_multiple(args.create[0])
  elif args.create_one:
    create_live_servers.create_one(args.create_one[0])
  elif args.delete == [] or args.delete:  #no argument is required
    delete_live_servers.delete_multiple()
  elif args.delete_one:
    delete_live_servers.delete_one(args.delete_one[0])
  elif args.move:
    admin_tools.move(args.move[0])
  elif args.enter:
    admin_tools.enter(args.enter[0])
  elif args.list == [] or args.list:  #no argument is required
    admin_tools.list(args.list)  #passes NetID if provided
  elif len(sys.argv) < 2:
    #more options can be created in main menu by appending to this array
    menu_options = ["Create server(s)", "Delete Server(s)", "Enter server", "Move server", "List servers"]
    main_menu(menu_options) #prints main menu
    user_choice = input("Pick an action: ")
    try:
      if not 0<int(user_choice)<6:
        print(f"{color.RED}[ERROR]{color.RESET} Invalid input.")
        exit()
    except: #Fails if user input is not an int
      print(f"{color.RED}[ERROR]{color.RESET} Invalid input.")
      exit()

    if user_choice =="1":
      create_live_servers.menu()
    elif user_choice == "2":
      delete_live_servers.menu()
    elif user_choice == "3":
      admin_tools.menu("enter")
    elif user_choice == "4":
      admin_tools.menu("move")
    elif user_choice == "5":
      admin_tools.menu("list")
    else:
      exit()
  else:
    raise Exception("Invalid arguments were chosen.")
    exit()
    
  
  
