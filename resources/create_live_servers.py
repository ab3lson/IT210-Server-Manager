import csv
import os
import subprocess
import shlex
import time

ADMIN_START_IP=50
ADMIN_START_VM_ID = 900
START_IP = 60     #This is the start of the last octet that will be used for students in 192.168.10.0/24
END_IP = 255
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


def next_admin_vm_id():
  cmd = "pct list | grep -e ^9 | awk 'END{print $1}'" #gets the last VM ID that starts with a 9 (admin range)
  return int(subprocess.check_output(cmd, shell=True).decode("utf-8")) + 1 #returns last admin VM ID + 1

def create(student, IP=START_IP, IS_ADMIN=0, END_IP=END_IP, ADMIN_START_IP=ADMIN_START_IP):
  if ADMIN_START_IP > int(IP) > END_IP:
    print(f"{color.RED}[ERROR]{color.RESET} Trying to create an IP out of the 192.168.10.50-255 range. Trying to create 192.168.10.{IP}.\nStopping!")
    exit()
  if IS_ADMIN:
    print(f"{color.YELLOW}[INFO]{color.RESET} Getting next admin VM ID ... ", end="")
    next_vm_id = next_admin_vm_id()
    print(color.YELLOW + str(next_vm_id) + color.RESET)
  else:
    next_vm_id = subprocess.run(['pvesh', 'get', '/cluster/nextid'], stdout=subprocess.PIPE).stdout.decode('utf-8')[:-1]
  return_val = os.system(f"""pct create {next_vm_id} \
                /var/lib/vz/template/cache/ubuntu-20.04-210-student-template.tar.gz \
                --cores 2 --cpuunits 2048 --memory 4096 --swap 512 \
                --hostname {student.netID}-210 \
                --net0 name=eth0,ip=192.168.10.{IP}/24,bridge=vmbr0,gw=192.168.4.1 \
                --rootfs local-lvm:16 \
                --onboot 1 --start 1
              """)
  if return_val != 0:
    print(f"{color.RED}[ERROR]{color.RESET} There was an issue creating a live server for {color.YELLOW + student.netID + color.RESET}! Please check the above error code and try again.")
    exit()
  print(f"{color.GREEN}[SUCCESS]{color.RESET} Account created for {color.YELLOW + student.netID + color.RESET}: ssh webadmin@192.168.10.{IP}!\n")

def check_ip(IP):
  cmd = f"ping -c 1 -w 3 192.168.10.{str(IP)}"
  return subprocess.call(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_next_IP(START_IP=START_IP, END_IP=END_IP):
  print(f"{color.BLUE}[WAIT]{color.RESET} Checking for next available IP address. Please wait...")
  for ip in range(START_IP, END_IP):
    res = check_ip(str(ip))
    if res != 0:
      print(f"{color.YELLOW}[INFO]{color.RESET} Confirming 192.168.10.{str(ip)} ... ", end='')
      second_res = check_ip(str(ip + 1))
      if second_res != 0:
        print(f"{color.GREEN}CONFIRMED!{color.RESET}")
        return ip
      print(f"{color.RED}FAILURE!{color.RESET}\nNext IP occupied.. Trying to find another!")
  print(f"{color.RED}[ERROR]{color.RESET} No empty IP addresses were found in 192.168.10.60-255. Please look into this and try again.")
  exit()

def create_multiple(FILENAME, START_IP=START_IP):
  student_list = []
  if ".csv" not in FILENAME:
    print(f"{color.RED}[ERROR]{color.RESET} The supplied filename, {FILENAME} does not appear to be a .csv file.")
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
            print(f"{color.RED}[ERROR]{color.RESET} students.csv was formatted incorrectly. At least one row probably has less than three values. \nThe problem is in the line starting with: {row[0]}:",e)
          except:
            print(f"{color.RED}[ERROR]{color.RESET} students.csv was formatted incorrectly. At least one row probably has less than three values. Problem:",e)
        student_list.append(temp_student)
        line_count += 1
  next_ip = int(get_next_IP(START_IP, END_IP))
  for student in student_list:
    create(student, next_ip)
    res = 0
    while not res:  #if ping returns 0, then the IP address is taken
      next_ip += 1
      print(f"{color.BLUE}[WAIT]{color.RESET} Verifying that 192.168.10.{str(next_ip)} is available. Please wait ... ", end="")
      if next_ip > 255:
        print(f"{color.RED}[FAIL]{color.RESET}\nAll IPs in 192.168.10.0/24 are taken.")
        exit()
      res = check_ip(str(next_ip))
      if res == 0:
        print(f"{color.RED}[FAIL]{color.RESET}")
    print(f"{color.GREEN}[SUCCESS]{color.RESET}")

  exit()


def create_one(NETID, START_IP=START_IP, END_IP=END_IP, ADMIN_START_IP=ADMIN_START_IP):
  temp_student = Student(NETID, NETID, NETID)
  IS_ADMIN = 0
  is_admin = input(f"{color.PURPLE}[QUESTION]{color.RESET} Is this an admin/TA account? (Y/N): ")
  if is_admin in ["Y","y"]:
    START_IP = ADMIN_START_IP
    END_IP = 59
    IS_ADMIN = 1
  next_ip = get_next_IP(START_IP, END_IP)
  print(f"{color.YELLOW}[INFO]{color.RESET} The next available IP address is: {color.BLUE}192.168.10.{next_ip + color.RESET}")
  custom_ip = input(f"{color.PURPLE}[QUESTION]{color.RESET} Do you want to use this IP address? (Y/N): ")
  if custom_ip in ["N","n"]:
    next_ip = input(f"Enter the last two digits of the IP address: 192.168.10.")
  create(temp_student, next_ip, IS_ADMIN)
  exit()

if __name__ == "__main__":
  FILENAME = input("What is the name of the .csv file?")
  create_servers(FILENAME)