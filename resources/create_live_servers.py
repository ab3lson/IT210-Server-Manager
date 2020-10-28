import csv
import os
import subprocess
import shlex
import time

ADMIN_START_IP=100
ADMIN_END_IP = 109
ADMIN_START_VM_ID = 900
START_IP = 110     #This is the start of the last octet that will be used for students in 192.168.90.0/24
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
  """
  Gets VM ID of next Virtual Machine above 900 (the admin range)
  """

  cmd = "pct list | grep -e ^9 | awk 'END{print $1}'" #gets the last VM ID that starts with a 9 (admin range)
  output = subprocess.check_output(cmd, shell=True).decode("utf-8")  #returns last admin VM ID
  if '9' not in output: return 900
  else: return int(output) + 1

def create(student, IP=START_IP, IS_ADMIN=False, END_IP=END_IP, ADMIN_START_IP=ADMIN_START_IP):
  """
  Creates a Virtual Machine using pct create and a custom IT 210 Ubuntu 20 image

  Parameters:
    student: a student class that contains the NetID, first name, and last name
    IP: The last octet of the IP address for the server (will be created in 192.168.90.0/24) (optional)
    IS_ADMIN: Boolean that states if the user will be given an admin VM ID (over 900). (optional)
    END_IP: The highest number that the last octet can go. Defaults to END_IP. (optional)
    ADMIN_START_IP: The starting IP for the admin IP addresses. Defaults to ADMIN_START_IP. (optional)
  """

  if ADMIN_START_IP > int(IP) > END_IP:
    print(f"{color.RED}[ERROR]{color.RESET} Trying to create an IP out of the 192.168.90.50-255 range. Trying to create 192.168.90.{IP}.\nStopping!")
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
                --net0 name=eth0,ip=192.168.90.{IP}/24,bridge=vmbr0,gw=192.168.4.1 \
                --rootfs local-lvm:16 \
                --onboot 1 --start 1
              """)
  if return_val != 0:
    print(f"{color.RED}[ERROR]{color.RESET} There was an issue creating a live server for {color.YELLOW + student.netID + color.RESET}! Please check the above error code and try again.")
    exit()
  print(f"{color.GREEN}[SUCCESS]{color.RESET} Account created for {color.YELLOW + student.netID + color.RESET}: ssh webadmin@192.168.90.{IP}!\n")

def check_ip(IP):
  """
  Checks if an IP address is active. Returns 0 for active, 1 for inactive.

  Parameters:
    IP: The last octet of the IP to ping
  """
  cmd = f"ping -c 1 -w 3 192.168.90.{str(IP)}"
  return subprocess.call(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_next_IP(START_IP=START_IP, END_IP=END_IP):
  """
  Checks for the next available IP range to start assigning IP addresses. If a free IP is found, it verifies
  that the following IP is also available.

  Parameters:
    START_IP: The last octet of the starting ping sweep range. Defaults to START_IP (optional)
    END_IP: The last octet of the ending ping sweep range. Defaults to END_IP (optional)
  """

  print(f"{color.BLUE}[WAIT]{color.RESET} Checking for next available IP address. Please wait...")
  for ip in range(START_IP, END_IP):
    res = check_ip(str(ip))
    if res != 0:
      print(f"{color.YELLOW}[INFO]{color.RESET} Confirming 192.168.90.{str(ip)} ... ", end='')
      second_res = check_ip(str(ip + 1))
      if second_res != 0:
        print(f"{color.GREEN}CONFIRMED!{color.RESET}")
        return ip
      print(f"{color.RED}FAILURE!{color.RESET}\nNext IP occupied.. Trying to find another!")
  print(f"{color.RED}[ERROR]{color.RESET} No empty IP addresses were found in 192.168.90.60-255. Please look into this and try again.")
  exit()

def create_multiple(FILENAME, START_IP=START_IP):
  """
  Creates multiple servers for students from a .csv.

  Parameters:
    FILENAME: The path to the .csv
    START_IP: The last octet for the start of the new servers' range. Defaults to START_IP. (optional)
  Notes:
    The first line of the .csv will be skipped to avoid using table headers.
    The .csv should follow the following format: LAST_NAME,FIRSTNAME,NETID
  """

  student_list = []
  if ".csv" not in FILENAME:
    print(f"{color.RED}[ERROR]{color.RESET} The supplied filename, {FILENAME} does not appear to be a .csv file.")
    exit()
  full_path = os.path.expanduser(FILENAME)
  with open(full_path) as student_csv:
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
      print(f"{color.BLUE}[WAIT]{color.RESET} Verifying that 192.168.90.{str(next_ip)} is available. Please wait ... ", end="")
      if next_ip > 255:
        print(f"{color.RED}[FAIL]{color.RESET}\nAll IPs in 192.168.90.0/24 are taken.")
        exit()
      res = check_ip(str(next_ip))
      if res == 0:
        print(f"{color.RED}[FAIL]{color.RESET}")
    print(f"{color.GREEN}[SUCCESS]{color.RESET}")

  exit()


def create_one(NETID, START_IP=START_IP, END_IP=END_IP, ADMIN_START_IP=ADMIN_START_IP, ADMIN_END_IP=ADMIN_END_IP):
  """
  Creates a server for the supplied NetID.

  Parameters:
    NETID: The NetID of the server to be created.
    START_IP: The start of the range that the IP could be. Defaults to START_IP. (optional)
    END_IP: The highest number that the last octet can go. Defaults to END_IP. (optional)
    ADMIN_START_IP: The starting IP for the admin IP addresses. Defaults to ADMIN_START_IP. (optional)
    ADMIN_END_IP: The ending IP for the admin IP addresses. Defaults to ADMIN_END_IP. (optional)
  """

  temp_student = Student(NETID, NETID, NETID)
  IS_ADMIN = 0
  is_admin = input(f"{color.PURPLE}[QUESTION]{color.RESET} Is this an admin/TA account? (Y/N): ")
  if is_admin in ["Y","y"]:
    START_IP = ADMIN_START_IP
    END_IP = ADMIN_END_IP
    IS_ADMIN = 1
  next_ip = get_next_IP(START_IP, END_IP)
  print(f"{color.YELLOW}[INFO]{color.RESET} The next available IP address is: {color.BLUE}192.168.90.{str(next_ip) + color.RESET}")
  custom_ip = input(f"{color.PURPLE}[QUESTION]{color.RESET} Do you want to use this IP address? (Y/N): ")
  if custom_ip in ["N","n"]:
    next_ip = input(f"Enter the last two digits of the IP address: 192.168.90.")
  create(temp_student, next_ip, IS_ADMIN)
  exit()

def menu():
  """
  Checks user option from main menu
  """
  user_choice = input(f"{color.PURPLE}[QUESTION]{color.RESET} Do you want to create more than one server? (Y/N): ")
  if user_choice in ["Y", "y"]:
    print(f"{color.BLUE}[INFO]{color.RESET} You can import a .csv file of students to create live servers for.\nIt should be in the following format: {color.YELLOW}LAST_NAME,FIRSTNAME,NETID{color.RESET}")
    FILENAME = input(f"{color.PURPLE}[QUESTION]{color.RESET} What is the path of the student list .csv file?")
    create_multiple(FILENAME)
  elif user_choice in ["N", "n"]:
    NETID = input(f"{color.PURPLE}[QUESTION]{color.RESET} What is the NetID that you want to create?): ")
    create_one(NETID)
  else: exit()


if __name__ == "__main__":
  menu()