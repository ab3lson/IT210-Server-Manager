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

def lxc_destory(container_id):
  cmd = f"lxc-destroy -f {container_id}"
  return subprocess.call(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def pct_destroy(container_id):
  cmd = f"pct destroy {container_id}"   # the lxc-destroy throws a 1 if this was the case
  return subprocess.call(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def pct_unlock(container_id):
  cmd = f"pct unlock {container_id}"
  return subprocess.call(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def delete(container_id, NETID="not supplied"):
  """
  Deletes one Virtual Machine at the specified VM ID.

  Parameters:
    contianer_id: The VM ID of the Virutal Machine to be deleted
    NETID: The NetID of the server to delete. For output only. (optional)
  """

  if int(container_id) < 100:
    print(f"{color.RED}[ERROR]{color.RESET} The container ID must be at least 100. Please try again.")
    return
  print(f"Starting deletion for {color.YELLOW + NETID + color.RESET}...")
  res = lxc_destory(container_id) #TODO Speed up: Try looping this command through the entire range and let them shut down together, then run pct destroy
  if res != 0 and res !=1:      #if there is an error
    print(f"{color.RED}[ERROR]{color.RESET} The server for {color.YELLOW + NETID + color.RESET} could not be deleted. Response code to lxc-destroy -f was {res} ")
    return
  elif res == 1:                          # if the container deletion failed the first time, it may have been shutting down still
    res = pct_destroy(container_id)
    if res == 255:
      print(f"{color.YELLOW}[INFO]{color.RESET} The server for {color.YELLOW + NETID + color.RESET} could not be deleted. It may be locked... trying \"pct unlock {container_id}\"")
      res = pct_unlock(container_id)
      if res != 0: return
      else: res = pct_destroy(container_id)
      if res != 0:
        print(f"{color.RED}[ERROR]{color.RESET} The server for {color.YELLOW + NETID + color.RESET} could not be deleted. Response code to pct destroy was {res}")
        return
    elif res != 0:
      print(f"\033[F{color.RED}[ERROR]{color.RESET} VM ID {color.YELLOW + str(container_id) + color.RESET} was not deleted. It was probably aleady deleted.")
      return
    print(f"\033[F{color.GREEN}[SUCCESS]{color.RESET} Server deleted for {color.YELLOW + NETID + color.RESET}!")
  else:          #if lxc-destroy worked and the container shut down, now it can be deleted from ProxMox
    print(f"{color.BLUE}[WAIT]{color.RESET} Shutting down container...")
    time.sleep(10)
    res = pct_destroy(container_id)
    if res != 0:
      print(f"""The server for {color.YELLOW + NETID + color.RESET} could not be deleted. The container may have been stopping, but didn't finish.
      Try again in a couple seconds or check the web GUI to see if it is still active.""")
      exit()
    print(f"\033[F\033[F{color.GREEN}[SUCCESS]{color.RESET} Server deleted for {color.YELLOW + NETID + color.RESET}!")

def delete_multiple():
  """
  Deletes multiple virtual machines. Asks user to supply range of VM IDs to delete.
  """

  RANGE_START = int(input(f"{color.PURPLE}[QUESTION]{color.RESET} What VM ID do you want to start at?: "))
  RANGE_END = int(input(f"{color.PURPLE}[QUESTION]{color.RESET} What VM ID do you want to end at?: ")) + 1
  confirm = input(f"Are you sure that you want to delete all servers between {color.BLUE + str(RANGE_START) + color.RESET} and {color.BLUE + str(int(RANGE_END - 1)) + color.RESET}? (Y/N): ")
  if not confirm in ['Y', 'y']:
    print("Whew! Exiting...")
    exit()
  to_delete = RANGE_START
  for student in range(RANGE_START, RANGE_END):
    delete(to_delete, "VM ID: " + str(to_delete))
    to_delete += 1
  print(f"\n{color.BLUE}[COMPLETE]{color.RESET} All servers between {color.BLUE + str(RANGE_START) + color.RESET} and {color.BLUE + str(RANGE_END - 1) + color.RESET} were deleted!")

def delete_one(NETID):
  """
  Deletes the Virtual Machine for the supplied NetID.

  Parameters:
    NETID: The NetID of the server to be deleted.
  """
  #match student netID to container ID
  container_id = get_vmid(NETID)
  confirm = input(f"Are you sure that you want to delete the account for {color.YELLOW + NETID + color.RESET} (VM ID: {color.YELLOW + str(container_id) + color.RESET})? (Y/N): ")
  if confirm in ['Y', 'y']:
    delete(container_id, NETID)
  else:
    exit()

def menu():
  """
  Checks user option from main menu
  """

  user_choice = input(f"{color.PURPLE}[QUESTION]{color.RESET} Do you want to delete more than one server? (Y/N): ")
  if user_choice in ["Y", "y"]:
    delete_multiple()
  elif user_choice in ["N", "n"]:
    NETID = input(f"{color.PURPLE}[QUESTION]{color.RESET} What is the NetID that you want to delete?: ")
    delete_one(NETID)

if __name__ == "__main__":
  menu()