import os
import subprocess
import shlex
import csv
import time

ADMIN_START_IP=50
START_IP = 60     #This is the start of the last octet that will be used for students in 192.168.10.0/24
END_IP = 255
class Student:
  def __init__(self, first_name, last_name, netID):
    self.first_name = first_name
    self.last_name = last_name
    self.netID = netID

class color:
  HEADER = '\033[95m'
  BLUE = '\033[94m'
  GREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  RESET = '\033[00m'

def get_vmid(NETID):
  #match student netID to container ID
  cmd = "pct list | tail -n+2 | awk '{print $1 \",\"$3}'"
  vm_ids = subprocess.check_output(cmd, shell=True).decode("utf-8") 
  container_info = [row for row in csv.reader(vm_ids.splitlines(), delimiter=',')]
  container_id = False
  for container in container_info:
    if container[1][:-6] == NETID:    #strips "Server" away from the container's hostname to see if it matches
      container_id = container[0]
  if not container_id:
    print(f"{color.FAIL}[ERROR]{color.RESET} The netID {NETID} could not be found. Please make sure that it exists and try again.")
    exit()
  return container_id

def lxc_destory(container_id):
  cmd = f"lxc-destroy -f {container_id}"
  return subprocess.call(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def pct_destroy(container_id):
  cmd = f"pct destroy {container_id}"   # the lxc-destroy throws a 1 if this was the case
  return subprocess.call(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def pct_unlock(container_id):
  cmd = f"pct unlock {container_id}"
  return subprocess.call(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def delete(container_id, NETID):
  if int(container_id) < 100:
    print(f"{color.FAIL}[ERROR]{color.RESET} The container ID must be at least 100. Please try again.")
    exit()
  print(f"Starting deletion for {NETID}...")
  res = lxc_destory(container_id)
  if res != 0 and res !=1:      #if there is an error
    print(f"{color.FAIL}[ERROR]{color.RESET} The server for {NETID} could not be deleted. Response code to lxc-destroy -f was {res} ")
    exit()
  elif res == 1:                          # if the container deletion failed the first time, it may have been shutting down still
    res = pct_destroy(container_id)
    if res == 255:
      print(f"{color.WARNING}[INFO]{color.RESET} The server for {NETID} could not be deleted. It may be locked... trying \"pct unlock {container_id}\"")
      res = pct_unlock(container_id)
      if res != 0: exit()
      else: res = pct_destroy(container_id)
      if res != 0:
        print(f"{color.FAIL}[ERROR]{color.RESET} The server for {NETID} could not be deleted. Response code to pct destroy was {res}")
        exit()
    elif res != 0:
      print(f"{color.FAIL}[ERROR]{color.RESET} The server for {NETID} could not be deleted.")
      exit()
    print(f"\033[F{color.GREEN}[SUCCESS]{color.RESET} Server deleted for {NETID}!")
  else:          #if lxc-destroy worked and the container shut down, now it can be deleted from ProxMox
    print(f"{color.BLUE}[WAIT]{color.RESET} Shutting down container...")
    time.sleep(10)
    cmd = f"pct destroy {container_id}"
    res = subprocess.call(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res != 0:
      print(f"""The server for {NETID} could not be deleted. The container may have been stopping, but didn't finish.
      Try again in a couple seconds or check the web GUI to see if it is still active.""")
      exit()
    print(f"\033[F\033[F{color.GREEN}[SUCCESS]{color.RESET} Server deleted for {NETID}!")

def delete_multiple():
  RANGE_START = int(input("What VM ID do you want to start at?:"))
  RANGE_END = int(input("What VM ID do you want to end at?:")) + 1
  confirm = input(f"Are you sure that you want to delete all servers between {RANGE_START} and {RANGE_END - 1}? (Y/N): ")
  if not confirm in ['Y', 'y']:
    print("Whew! Exiting...")
    exit()
  to_delete = RANGE_START
  for student in range(RANGE_START, RANGE_END):
    delete(to_delete, "VM ID:" + str(to_delete))
    to_delete += 1
  print(f"All servers between {RANGE_START} and {RANGE_END} were deleted!")

def delete_one(NETID):
  #match student netID to container ID
  container_id = get_vmid(NETID)
  confirm = input(f"Are you sure that you want to delete the account for {NETID} (VM ID: {container_id})? (Y/N): ")
  if confirm in ['Y', 'y']:
    delete(container_id, NETID)
  else:
    exit()


if __name__ == "__main__":
  START_IP = input("What VM ID do you want to start at?:")
  END_IP = input("What VM ID do you want to end at?:")