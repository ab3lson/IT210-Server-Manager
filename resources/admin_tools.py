import os
import subprocess
import shlex
import csv
import time


class Student:
  def __init__(self, first_name, last_name, netID):
    self.first_name = first_name
    self.last_name = last_name
    self.netID = netID

class color:
  PURPLE = '\033[95m'
  BLUE = '\033[94m'
  GREEN = '\033[92m'
  YELLOW = '\033[93m'
  RED = '\033[91m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  RESET = '\033[00m'

def get_vmid(NETID):
  """
  Maps the supplied NetID to a Virtual Machine ID.

  Parameters:
    NETID: The NetID to get the VM ID for
  """

  cmd = "pct list | tail -n +2 | awk '{sub(/-210/,\"\"); print $1 \",\"$3}'"
  vm_ids = subprocess.check_output(cmd, shell=True).decode("utf-8") 
  container_info = [row for row in csv.reader(vm_ids.splitlines(), delimiter=',')]
  container_id = False
  for container in container_info:
    if container[1] == NETID:
      return container[0]
  if not container_id:
    print(f"{color.RED}[ERROR]{color.RESET} The NetID {color.YELLOW + NETID + color.RESET} could not be found. Please make sure that it exists and try again.")
    exit()

def list(NETID="all_students"):
  """
  Uses the pct list command to get Virtual Machine IDs. 
  If no params are given, then all VM IDs and NetIDs are given.
  
  Parameters:
    NETID: The NetID of the student to look up (optional)
  """

  if NETID != "all_students":
    #match student netID to container ID
    container_id = get_vmid(NETID)
    print(f"NetID\t\tVM ID\n-----\t----\n{NETID}\t{container_id}")
  else:
    cmd = "pct list | tail -n +2 | awk '{sub(/-210/,\"\"); print $1 \"    \"$3}'"
    print(f"VM ID\tNetID\n-----\t----")
    print(subprocess.check_output(cmd, shell=True).decode("utf-8"))

def enter(NETID):
  """
  Enters the Virtual Machine for the supplied NetID.

  Parameters:
    NETID: The NetID of the server to enter
  """

  vm_id = get_vmid(NETID)
  print(f"{color.YELLOW}[INFO]{color.RESET} Entering {color.YELLOW + NETID + color.RESET} (VM ID: {vm_id})... Press {color.PURPLE}ctrl + d{color.RESET} to exit!")
  cmd = f"pct enter {vm_id}"
  subprocess.run(shlex.split(cmd))

def move(NETID, container_id=False, new_vm_id=False):
  """
  Moves a Virtual Machine to a new VM ID.

  Parameters:
    NETID: The NetID of the server to move
    container_id: The current VM ID of the Virtual Machine (optional)
    new_vm_id: The new VM ID that the server will be moved to (optional)
  Notes:
    Admin/TA range starts at VM ID 900. This makes VM management easier, because
    student VM IDs are separated from Admin VM IDs.
  """

  if not container_id and not new_vm_id: #gets info from user, if it was not supplied
    new_vm_id = input(f"{color.PURPLE}[QUESTION]{color.RESET} What do you want their new VM ID to be? (Admin/TA range starts at 900): ")
    container_id = get_vmid(NETID)
  print(f"{color.YELLOW}[INFO]{color.RESET} Stopping {color.YELLOW + NETID + color.RESET}\'s live server (VM ID: {container_id}) ... ", end='')
  cmd = f"pct stop {container_id}"
  res = subprocess.call(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  time.sleep(3)
  if res != 0:
    print(f"{color.RED}[FAIL]{color.RESET}\n The container could not be stopped.")
    exit()
  else: print(f"{color.GREEN}[SUCCESS]{color.RESET}")
  print(f"{color.YELLOW}[INFO]{color.RESET} Cloning VM ID {color.YELLOW + str(container_id) + color.RESET} to {color.YELLOW + str(new_vm_id) + color.RESET} ... ", end='')
  cmd = f"pct clone {container_id} {new_vm_id}"
  res = subprocess.call(shlex.split(cmd), stdout=subprocess.PIPE)
  time.sleep(3)
  if res != 0:
      print(f"{color.RED}[FAIL]{color.RESET}\n The container could not be cloned.")
      print(f"{color.YELLOW}[INFO]{color.RESET} Restarting old container...")
      cmd = f"pct start {container_id}"
      res = subprocess.call(shlex.split(cmd), stdout=subprocess.PIPE)
      exit()
  else: print(f"{color.GREEN}[SUCCESS]{color.RESET}")
  print(f"{color.YELLOW}[INFO]{color.RESET} Deleting VM ID {color.YELLOW + str(container_id) + color.RESET} ... ", end='')
  cmd = f"pct destroy {container_id}"
  res = subprocess.call(shlex.split(cmd), stdout=subprocess.PIPE)
  time.sleep(3) 
  if res != 0:
      print(f"{color.RED}[FAIL]{color.RESET}\n The container could not be deleted.")
      exit()
  else: print(f"{color.GREEN}[SUCCESS]{color.RESET}")
  print(f"{color.YELLOW}[INFO]{color.RESET} Starting new VM ID {color.YELLOW + str(new_vm_id) + color.RESET} ... ", end='')
  cmd = f"pct start {new_vm_id}"
  res = subprocess.call(shlex.split(cmd), stdout=subprocess.PIPE)
  time.sleep(3)
  if res != 0:
      print(f"{color.RED}[FAIL]{color.RESET}\n The new container could not be started.")
      exit()
  else: print(f"{color.GREEN}[SUCCESS]{color.RESET}")
  print(f"{color.YELLOW}[INFO]{color.RESET} The IP address is still the same. If you want to edit this, you can do so in the network settings for the VM at the Proxmox web GUI:\nhttps://192.168.10.41:8006/")

def menu(menu_opt="none"):
  """
  Checks user option from main menu
  """
  if menu_opt == "move":
    NETID = input(f"{color.PURPLE}[QUESTION]{color.RESET} What is the NetID that you would like to move?: ")
    move(NETID)
  elif menu_opt == "enter":
    NETID = input(f"{color.PURPLE}[QUESTION]{color.RESET} What is the NetID that you would like to enter?: ")
    enter(NETID)
  elif menu_opt == "list":
    list()
  else: exit()