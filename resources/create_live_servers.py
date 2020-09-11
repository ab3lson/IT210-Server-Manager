import csv
import os
import subprocess

class Student:
  def __init__(self, first_name, last_name, netID):
    self.first_name = first_name
    self.last_name = last_name
    self.netID = netID

def create_servers(FILENAME):
  student_list = []
  if ".csv" not in FILENAME:
    print(f"ERROR: The supplied filename, {FILENAME} does not appear to be a .csv file.")
    exit()
  with open(FILENAME) as student_csv:
    reader = csv.reader(student_csv, delimiter=',')
    line_count = 0
    for row in reader:
      if line_count == 0:
        line_count += 1
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
    print("First Name:",student.first_name, "\tLast Name:", student.last_name, "\tNetID:", student.netID)

  START_IP = 60
  testing = Student("TEST", "STUDENT", "SCRIPTED")
  student_list = [testing]

  next_vm_id = subprocess.run(['pvesh', 'get', '/cluster/nextid'], stdout=subprocess.PIPE).stdout.decode('utf-8')[:-1]

  for student in student_list:
    return_val = os.system(f"""pct create {next_vm_id} \
                /var/lib/vz/template/cache/ubuntu-20.04-standard_20.04-1_amd64.tar.gz \
                --cores 2 --cpuunits 2048 --memory 4096 --swap 512 \
                --hostname {student.netID}Server \
                --net0 name=eth0,ip=192.168.10.{START_IP}/24,bridge=vmbr0,gw=192.168.4.1 \
                --rootfs local-lvm:16 \
                --onboot 1
              """)
    if return_val != 0:
      print(f"ERROR: There was an issue creating a live server for {student.netID}! Please check the above error code and try again.")
      exit()
    
    # subprocess.Popen(["ptc", "enter", next_vm_id])

    START_IP += 1

  # TODO: Create an iso image with a default user and password and create a container from that!

if __name__ == "__main__":
  FILENAME = input("What is the name of the .csv file?")
  create_servers(FILENAME)