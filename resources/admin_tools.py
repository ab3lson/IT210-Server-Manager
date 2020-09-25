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


def get_vmid(NETID):
  cmd = "pct list | tail -n +2 | awk '{sub(/-210/,\"\"); print $1 \"    \"$3}'"
  vm_ids = subprocess.check_output(cmd, shell=True).decode("utf-8") 
  container_info = [row for row in csv.reader(vm_ids.splitlines(), delimiter=',')]
  container_id = False
  for container in container_info:
    print("container:",container)
    if container[1][:-4] == NETID:    #strips "-210" away from the container's hostname to see if it matches
      return container[0]
  if not container_id:
    print(f"The netID {NETID} could not be found. Please make sure that it exists and try again.")
    exit()

def list(NETID):
  if NETID != "all_students":
    #match student netID to container ID
    container_id = get_vmid(NETID)
    print(f"NetID\tVM ID\n-----\t----\n{NETID}\t{container_id}")
  else:
    cmd = "pct list | tail -n +2 | awk '{sub(/-210/,\"\"); print $1 \"    \"$3}'"
    print(f"NetID\tVM ID\n-----\t----")
    print(subprocess.check_output(cmd, shell=True).decode("utf-8"))

def enter(NETID):
  vm_id = get_vmid(NETID)
  print(f"{color.YELLOW}[INFO]{color.RESET} Entering {color.YELLOW + NETID + color.RESET} (VM ID: {vm_id})... Press {color.PURPLE}ctrl + d{color.RESET} to exit!")
  cmd = f"pct enter {vm_id}"
  subprocess.run(shlex.split(cmd))