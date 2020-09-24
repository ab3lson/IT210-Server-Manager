import os
import subprocess
import shlex
import csv
import time


START_IP = 60     #This is the start of the last octet that will be used for students in 192.168.10.0/24
END_IP = 255
class Student:
  def __init__(self, first_name, last_name, netID):
    self.first_name = first_name
    self.last_name = last_name
    self.netID = netID

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
    print(f"The netID {NETID} could not be found. Please make sure that it exists and try again.")
    exit()
  return container_id

def delete(container_id, NETID):
  cmd = f"lxc-destroy -f {container_id}"
  res = subprocess.call(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  if res != 0 and res !=1:      #if there is an error
    print(f"The server for {NETID} could not be deleted.")
    exit()
  elif res == 1:                          # if the container deletion failed the first time, it may have been shutting down still
    cmd = f"pct destroy {container_id}"   # the lxc-destroy throws a 1 if this was the case
    res = subprocess.call(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res != 0:
      print(f"The server for {NETID} could not be deleted.")
      exit()
  else:          #if lxc-destroy worked and the container shut down, now it can be deleted from ProxMox
    print("Waiting 10 seconds per machine for shutdown.")
    time.sleep(10)
    cmd = f"pct destroy {container_id}"
    res = subprocess.call(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res != 0:
      print(f"""The server for {NETID} could not be deleted. The container may have been stopping, but didn't finish.
      Try again in a couple seconds or check the web GUI to see if it is still active.""")
      exit()
    print(f"Server deleted for {NETID}!")

def delete_multiple(START_IP=START_IP, END_IP=END_IP):
  RANGE_START = input("What IP do you want to start at?: 192.168.10.")
  RANGE_START = input("What IP do you want to end at?: 192.168.10.")
  confirm = input(f"Are you sure that you want to delete all servers between 192.168.10.{RANGE_START}-{RANGE_END}? (Y/N): ")
  if not confirm in ['Y', 'y']:
    print("Whew! Exiting...")
    exit()
  for student in range(START_IP,END_IP):
    
    pass


def delete_one(NETID):
  #match student netID to container ID
  container_id = get_vmid(NETID)
  confirm = input(f"Are you sure that you want to delete the account for {NETID} (VM ID: {container_id})? (Y/N): ")
  if confirm in ['Y', 'y']:
    delete(container_id, NETID)
  else:
    exit()


if __name__ == "__main__":
  START_IP = input("What is the start of the IP range to delete?: 192.168.10.")
  END_IP = input("What is the end of the IP range to delete?: 192.168.10.")