import csv
import os
import subprocess

START_IP = 60     #This is the start of the last octet that will be used for students in 192.168.10.0/24
END_IP = 255
class Student:
  def __init__(self, first_name, last_name, netID):
    self.first_name = first_name
    self.last_name = last_name
    self.netID = netID

def create(student, IP=START_IP):
  if IP > END_IP:
    print(f"ERROR: Trying to create an IP out of the 192.168.10.0/24 subnet. Trying to create 192.168.10.{IP}.\nStopping!")
    exit()
  next_vm_id = subprocess.run(['pvesh', 'get', '/cluster/nextid'], stdout=subprocess.PIPE).stdout.decode('utf-8')[:-1]
  return_val = os.system(f"""pct create {next_vm_id} \
                /var/lib/vz/template/cache/ubuntu-20.04-210-student-template.tar.gz \
                --cores 2 --cpuunits 2048 --memory 4096 --swap 512 \
                --hostname {student.netID}Server \
                --net0 name=eth0,ip=192.168.10.{IP}/24,bridge=vmbr0,gw=192.168.4.1 \
                --rootfs local-lvm:16 \
                --onboot 1
              """)
  if return_val != 0:
    print(f"ERROR: There was an issue creating a live server for {student.netID}! Please check the above error code and try again.")
    exit()

def get_next_IP(START_IP=START_IP, END_IP=END_IP):
  print("Checking for next available IP address... Please wait")
  for ip in range(START_IP, END_IP):
    res = subprocess.call(['ping', '-c', '3', "192.168.10." + str(ip)])
    if res != 0:
      print(f"192.168.10.{str(ip)} should be open... Checking next IP to confirm.")
      second_res = subprocess.call(['ping', '-c', '3', "192.168.10." + str(ip + 1)])
      if second_res == 0:
        print(f"192.168.10.{str(ip)} confirmed!")
        return "192.168.10." + str(ip)
      print("Next IP occupied.. Trying to find another!")
  print("ERROR: No empty IP addresses were found in 192.168.10.60-255. Please look into this and try again.")
  exit()


def create_multiple(FILENAME):
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
  
  for student in student_list:
    create(student)
    next_vm_id += 1
    START_IP += 1


def create_one(NETID):
  temp_student = Student(NETID, NETID, NETID)
  is_admin = input("Is this an admin/TA account? (Y/N")
  if is_admin in ["Y","y"]:
    START_IP = 50
    END_IP = 59
  next_ip = get_next_IP(START_IP, END_IP)
  custom_ip = input(f"The next available IP address is: {next_ip} Do you want a different IP address? (Y/N)")
  if custom_ip in ["Y","y"]:
    custom_ip = input(f"Enter the last two digits of the IP address: 192.168.10.")
    create(temp_student, custom_ip)
  else: create(temp_student, next_ip)


if __name__ == "__main__":
  FILENAME = input("What is the name of the .csv file?")
  create_servers(FILENAME)