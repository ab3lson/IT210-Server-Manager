import os
import subprocess
import shlex
import csv


START_IP = 60     #This is the start of the last octet that will be used for students in 192.168.10.0/24
END_IP = 255
class Student:
  def __init__(self, first_name, last_name, netID):
    self.first_name = first_name
    self.last_name = last_name
    self.netID = netID


def delete_multiple(START_IP=START_IP, END_IP=END_IP):
  
  for student in range(START_IP,END_IP):
    #pct destroy <CONTAINER ID>
    pass


def delete_one(NETID):
  #match student netID to container ID
  cmd = "pct list | tail -n+2 | awk '{print $1 \", \"$3}'"
  vm_ids = subprocess.check_output(cmd, shell=True).decode("utf-8") 
  container_info = [row for row in csv.reader(x.splitlines(), delimiter=',')]
  container_id = False
  for container in container_info:
    if container[1] == NETID:
      container_id = container[0]
  if not container_id:
    print(f"The netID {NETID} could not be found. Please make sure that it exists and try again.")
    exit()
  confirm = input(f"Are you sure that you want to delete the account for {NETID} (VM ID: {container_id})? (Y/N): ")
  if confirm in ['Y', 'y']:
    cmd = f"pct destroy {container_id}"
    res = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE)
    if res != 0:
      print(f"The server for {NETID} could not be deleted.")
      exit()
    print(f"Server deleted for {NETID}!")
  else:
    exit()


if __name__ == "__main__":
  START_IP = input("What is the start of the IP range to delete?: 192.168.10.")
  END_IP = input("What is the end of the IP range to delete?: 192.168.10.")

test = '''"df /dev/sda1 | awk /'NR==2 {sub("%","",$5); if ($5 >= 80) {printf "Warning! Space usage is %d%%", $5}}"'''
cmd = "pct list | tail -n+2 | awk '{print $1 \", \"$3}'"