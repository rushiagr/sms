#! /usr/bin/env python

import commands
from operator import attrgetter
import re

cont = {}       # Dictionary to hold all the contacts as (number, name) pair
ls = []         # List to hold the Msg objects. It will contain msg objects of
                # all the message files to be processed
currdict = {}   # Will hold all the msg objects as (date, msg) pair which are to
                # be written in one single metadata file


# Class for holding a message
class Msg:
    def show(self):
        print self.type, self.date, self.phone, self.content

# Extracts all the messages from the csv file
def extract_csv(msgfilename):
    msgfilename = 'to_process/' + msgfilename[0:len(msgfilename)-1]
    f = open(msgfilename,'r')
    mlist = []
    for line in f:
        msg = Msg()
#        print line
        if line == 'sms,"","","","","",""\n' or line == 'sms,"","","","","",""':
            break
        if line[4] == 'd':
            msg.type = 'i'
            line = line.split('","","","')
            msg.date = int(line[1][0:4]+line[1][5:7]+line[1][8:10]+line[1][11:13]+line[1][14:16]+'00')
            msg.content = line[1][22:len(line[1])-2]
            msg.phone = line[0].split(',"')[1]
        elif line[4] == 's':
            msg.type = 's'
            line = line[15:len(line)]
            line = line.split('","","')
            msg.phone = line[0]
            msg.date = int(line[1][0:4]+line[1][5:7]+line[1][8:10]+line[1][11:13]+line[1][14:16]+'00')
#            print msg.date
            msg.content = line[2][0:len(line[2])-2]
        if msg.phone.isdigit():
            msg.phone = int(msg.phone)
        elif msg.phone[0:3] == '+91':
            msg.phone = int(msg.phone[3:len(msg.phone)])
        mlist.append(msg)
#    print mlist
    return mlist

# Returns Msg object which contains all the information of message file given
# as input parameter
def extract_vmg(msgfilename):
  msgfilename = 'to_process/' + msgfilename[0:len(msgfilename)-1]
  f = open(msgfilename, 'r')
  msg = Msg()
  msg.content = ''
  msg.phone = -1
  count = 0;
  for line in f:
    line = "".join(str(n) for n in line[1::2])
    count = count + 1
    if count == 5:
      templist = line.strip("X-NOK-DT:").strip('Z\n').rsplit('T')
      msg.date = int(templist[0] + templist[1])
    if count == 6:
      if line.endswith('DELIVER\n'):
        msg.type = 'i'          # i for inbox
      elif line.endswith('SUBMIT\n'):
        msg.type = 's'          # s for sent
      elif line.endswith(':\n'):
        msg.type = 'x'          # unknown type, used for error checking
      else:
        print 'error in submit/sent\n'
    if count > 6:
      if msg.type == 'i':
        if count == 10:
          if line == 'TEL:\n':
            msg.phone = 1111111111
          elif len(line) == 18 and line[0:7] == 'TEL:+91':
            msg.phone = int(line[7:17])
          elif len(line) == 15 and line[0:4] == 'TEL:' and line[4:14].isdigit():
            msg.phone = int(line[4:14])
          elif len(line) < 15 and line[0:4] == 'TEL:':
            if(line[4:len(line)-1].isdigit()):
              msg.phone = int(line[4:len(line)-1])
            else:
              msg.phone = line[4:len(line)-1]
        if count >= 15 and line != 'END:VBODY\n':
          msg.content = msg.content + line
        elif line == 'END:VBODY\n':
          break
      if msg.type == 's':
        if count == 16:
          if line == 'TEL:\n':
            msg.phone = 'DRAFT'
          elif len(line) == 18 and line[0:7] == 'TEL:+91':
            msg.phone = int(line[7:17])
          elif len(line) == 15 and line[0:4] == 'TEL:':
            msg.phone = int(line[4:14])
          elif len(line) < 15 and line[0:4] == 'TEL:':
            if(line[4:len(line)-1].isdigit()):
              msg.phone = int(line[4:len(line)-1])
            else: msg.phone = line[4:len(line)-1]
        if count >= 21 and line != 'END:VBODY\n':
          msg.content = msg.content + line
        elif line == 'END:VBODY\n':
          break
  f.close()
  return msg

# Checks if the specified file/directory exists or not. Returns true if the
# file exists
def exist(filename):
    if(len(commands.getoutput('if [ -e '+filename+' ];then echo "YES";fi')) > 0):
        return False
    else:
        return False

# Add the name and number to cont if not present. The contact name is taken
# from the .vmg file, and the phone number is taken from the msgobj object
def addtocont(msgfilename, msgobj):
  if msgfilename.find('_') != -1 or msgfilename.find('-') != -1:
    """ This will ensure that the .vmg files which are copied from a backup file
    (using say nbuexplorer), which do not contain a contact 'name', are also
    readable through this program"""
    if msgfilename[0].isdigit():
      if not msgobj.phone in cont:
        cont[msgobj.phone] = ''
    elif msgfilename[0] == '+':
      if not msgobj.phone in cont:
        cont[msgobj.phone] = ''
    elif msgfilename[0].isalpha():
      cont[msgobj.phone] = msgfilename.split('_')[0]
  else: cont[msgobj.phone] = ''

# Returns <phone number>_<year> of the msg object. This will be the file name
# of the metafile of the contact
def metafilename(msg):
    return 'conversations/' + str(msg.phone) + '_' + str(msg.date)[0:4] + '.html'


# Returns list of msg objects. Loads all the messages from the specified
# conversation file into the memory.
def load(filename):
  msglist = []
  if exist(filename):
#    print '"', filename, '" exists!'
    fileparts = re.compile(r'[/_.]').split(filename)
    if fileparts[1].isdigit():
      ph = int(fileparts[1])
    else: ph = fileparts[1]
    f = open(filename, 'r')
    l = f.readline()
    l = l[4:len(l)-4].split('|')
    msgnum = int(l[3])
    for i in range(0,102):
      l = f.readline()
    l = f.readline()
    for i in range(0,msgnum):
      msg = Msg()
      msg.phone = ph
      msg.content = ''
      l = f.readline()
      while l[0:6] != '</div>':
        msg.content += l[0:len(l)-5] + '\n'
        l = f.readline()
      l = f.readline()
      if len(l) <= 20:
        msg.type = 'i'
      else: msg.type = 's'
      l = re.compile(r'[- :]').split(l)
#      print l
      msg.date = int(l[2]+l[1]+l[0]+l[3]+l[4]+l[5])
      msglist.append(msg)
      l = f.readline()
      l = f.readline()
      l = f.readline()
  return msglist


# Dumps all the information in the dictionary to the given filename.
def dumptofile(dic, filename):
  sortorder = sorted(dic)
  f = open(filename, 'w')
  fileparts = re.compile(r'[/_.]').split(filename)
  if fileparts[1].isdigit():
    f.write('<!--' + cont[int(fileparts[1])] + '|' + fileparts[1] + '|' + filename.split('_')[1] + '|' + str(len(sortorder)) + '|v1' + '-->\n')
  else:
    f.write('<!--|' + fileparts[1] + '|' + filename.split('_')[1] + '|' + str(len(sortorder)) + '|v1' + '-->\n')
  f.close()
  fhtmlstart = open('src/start_code', 'r')
  f = open(filename, 'a')
  l = fhtmlstart.readlines()
  l = ''.join(l)
  f.write(l)
  fhtmlstart.close()
  f.write('<div class="heading">\n')
  if fileparts[1].isdigit():
    f.write(cont[int(fileparts[1])] + '\n')
  else:
    f.write('\n')
  f.write('</div>\n')
  f.write('<div class="number">\n')
  f.write(fileparts[1] + '\n')
  f.write('</div>\n')
  f.write('<div class="subHeading">\n')
  f.write(str(len(sortorder)) + '\n')
  f.write('messages, year\n')
  f.write(fileparts[2] + '\n')
  f.write('<br><br></div>\n')
  for i in sortorder:
    f.write(formattedmsg(dic[i]))
  f.write('<div class="copyright" >&#169\n') 
  f.write('<a href="mailto:rushi.agr@gmail.com">Rushi Agrawal</a></div>\n')
  f.write('</div>\n')
  f.write('</body>\n')
  f.write('</html>\n')
  f.close()
  if fileparts[1].isdigit():
    print 'Writing of ' + fileparts[1] + '-' + cont[int(fileparts[1])] + ' done'

# Returns string, the format in which the message is to be written
# to message data file
def formattedmsg(msg):
  string = ''
  if msg.type == 'i':
    string = '<div class="divContainerDownLeft">\n'
  elif msg.type == 's':
    string = '<div class="divContainerDownRight">\n'
  for i in msg.content.split('\n'):
    string += i + '<br>\n'
  string = string[0:len(string)-5]
  if msg.type == 'i':
    string += '</div><div style="clear:both;"></div><div class="infoLeft">\n'
  elif msg.type == 's':
    string += '</div><div style="clear:both;"></div><div class="infoRight">\n'
  string += str(msg.date)[6:8] + '-' + str(msg.date)[4:6] + '-' + str(msg.date)[0:4] + ' ' + str(msg.date)[8:10] + ':' + str(msg.date)[10:12] + ':' + str(msg.date)[12:14]
 # print msg.date, 'ooh!!'
  if msg.type == 'i':
    string += '\n</div>\n\n'
  elif msg.type == 's':
    string += ' (You)\n</div>\n\n'
  return string


commands.getoutput('ls -1 to_process > meta/msgfiles')
if not exist('meta/contacts'):
    commands.getoutput('echo "" > meta/contacts')

# Loading all contacts in memory (in cont)
f = open('meta/contacts', 'r')
for line in f:
  contactparts = line.split('|')
  if line != '\n':
    if contactparts[0].isdigit():
      cont[int(line.split('|')[0])] = line.split('|')[1][0:len(line.split('|')[1])-1]
    else: cont[line.split('|')[0]] = line.split('|')[1][0:len(line.split('|')[1])-1]
f.close()


################################
## Main execution begins here ##
################################

# Getting all the information from the message files into list ls
f = open('meta/msgfiles', 'r')
for line in f:
    if line.endswith('.vmg\n'):
        msgobj = extract_vmg(line)
        if msgobj.type != 'x':
            ls.append(extract_vmg(line))
            if ls[len(ls)-1].phone == -1:
                del ls[len(ls)-1]
            else:
                addtocont(line, ls[len(ls)-1])
    if line.endswith('.csv\n'):
#        print 'peep'
        csv_list = extract_csv(line)
 #       print csv_list
        for i in csv_list:
            if not cont.has_key(i.phone):
                cont[i.phone]=''
        ls.extend(csv_list)


print 'info of ', len(ls), ' files into memory now'
f.close()

# Sorting that list, first by phone number, and then by date
ls =  sorted(ls, key=attrgetter('phone', 'date'))

# For each contact, all the messages in the same year (from both, .vmg message
# files and the metafile of the same contact) are loaded in a separate
# dictionary currdict, and then put back again in the metafile
nextindex = 0   # Index upto which the ls list is searched
while nextindex < len(ls):
    currdict = {}
    currdict[ls[nextindex].date] = ls[nextindex]
    if nextindex < len(ls)-2:
        while metafilename(ls[nextindex]) == metafilename(ls[nextindex+1]):
            nextindex = nextindex + 1
            if nextindex >= len(ls)-1:
                break
            currdict[ls[nextindex].date] = ls[nextindex]
        currdict[ls[nextindex].date] = ls[nextindex]
    donemsgs = load(metafilename(ls[nextindex]))
    if len(donemsgs) > 0:
        for i in donemsgs:
            currdict[i.date] = i
#   print "next index metafile:"
#   print metafilename(ls[nextindex])
    dumptofile(currdict, metafilename(ls[nextindex]))
    nextindex = nextindex + 1

# Writing back all contacts to contacts file
towrite = ''
for i in cont:
    towrite = towrite + str(i) + '|' + str(cont[i]) + '\n'
f = open('meta/contacts', 'w')
f.write(towrite)

# Moving all the processed msg files to processed folder
commands.getoutput('mv -f to_process/* processed/')
