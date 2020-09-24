import csv
import os
import subprocess
import shlex
import time

ADMIN_START_IP=50
START_IP = 60     #This is the start of the last octet that will be used for students in 192.168.10.0/24
END_IP = 255
class Student:
  def __init__(self, first_name, last_name, netID):
    self.first_name = first_name
    self.last_name = last_name
    self.netID = netID

def create(student, IP=START_IP, END_IP=END_IP, ADMIN_START_IP=ADMIN_START_IP):
  if ADMIN_START_IP > int(IP) > END_IP:
    print(f"ERROR: Trying to create an IP out of the 192.168.10.50-255 range. Trying to create 192.168.10.{IP}.\nStopping!")
    exit()
  next_vm_id = subprocess.run(['pvesh', 'get', '/cluster/nextid'], stdout=subprocess.PIPE).stdout.decode('utf-8')[:-1]
  return_val = os.system(f"""pct create {next_vm_id} \
                /var/lib/vz/template/cache/ubuntu-20.04-210-student-template.tar.gz \
                --cores 2 --cpuunits 2048 --memory 4096 --swap 512 \
                --hostname {student.netID}Server \
                --net0 name=eth0,ip=192.168.10.{IP}/24,bridge=vmbr0,gw=192.168.4.1 \
                --rootfs local-lvm:16 \
                --onboot 1 --start 1
              """)
  if return_val != 0:
    print(f"ERROR: There was an issue creating a live server for {student.netID}! Please check the above error code and try again.")
    exit()
  print(f"Account created for {student.netID}: ssh webadmin@192.168.10.{IP}!")


def get_next_IP(START_IP=START_IP, END_IP=END_IP):
  print("Checking for next available IP address. Please wait...")
  for ip in range(START_IP, END_IP):
    cmd = f"ping -c 1 -w 1 192.168.10.{str(ip)}"
    res = subprocess.run(shlex.split(cmd), stdout=subprocess.DEVNULL)
    if res != 0:
      print(f"Confirming 192.168.10.{str(ip)} ... ", end='')
      cmd = f"ping -c 1 -w 1 192.168.10.{str(ip + 1)}"
      second_res = subprocess.run(shlex.split(cmd), stdout=subprocess.DEVNULL)
      if second_res != 0:
        print("CONFIRMED!")
        return "192.168.10." + str(ip)
      print("FAILURE!\nNext IP occupied.. Trying to find another!")
  print("ERROR: No empty IP addresses were found in 192.168.10.60-255. Please look into this and try again.")
  exit()


def create_multiple(FILENAME, START_IP=START_IP):
  student_list = []
  if ".csv" not in FILENAME:
    print(f"ERROR: The supplied filename, {FILENAME} does not appear to be a .csv file.")
    exit()
  with open(FILENAME) as student_csv:
    reader = csv.reader(student_csv, delimiter=',')
    line_count = 0
    for row in reader:
      if line_count == 0:
        line_count += 1   #jumps the reader ahead one row
      else:
        try:
          temp_student = Student(row[1], row[0], row[2])
        except IndexError as e:
          try:
            print(f"ERROR: students.csv was formatted incorrectly. At least one row probably has less than three values. \nThe problem is in the line starting with: {row[0]}:",e)
          except:
            print("ERROR: students.csv was formatted incorrectly. At least one row probably has less than three values. Problem:",e)
        student_list.append(temp_student)
        line_count += 1
  for student in student_list:
    print("First Name:", student.first_name, "\tLast Name:", student.last_name, "\tNetID:", student.netID)
  
  next_ip = get_next_IP(START_IP, END_IP)
  for student in student_list:
    create(student, next_ip[-2:])
    START_IP += 1
  exit()


def create_one(NETID, START_IP=START_IP, END_IP=END_IP, ADMIN_START_IP=ADMIN_START_IP):
  temp_student = Student(NETID, NETID, NETID)
  is_admin = input("Is this an admin/TA account? (Y/N): ")
  if is_admin in ["Y","y"]:
    START_IP = ADMIN_START_IP
    END_IP = 59
  next_ip = get_next_IP(START_IP, END_IP)
  custom_ip = input(f"The next available IP address is: {next_ip} Do you want to use this IP address? (Y/N): ")
  if custom_ip in ["N","n"]:
    next_ip = "192.168.10." + input(f"Enter the last two digits of the IP address: 192.168.10.")
  create(temp_student, next_ip[-2:])
  exit()

if __name__ == "__main__":
  FILENAME = input("What is the name of the .csv file?")
  create_servers(FILENAME)