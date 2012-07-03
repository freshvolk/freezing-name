import urllib
import urllib2
import simplejson as json
import time
import codecs
import operator

print "Output file will OVERWRITE other files w/o confirmation"
filenamein = raw_input("Name of input file: ")
filenameout = raw_input("Name of output file: ")

raw_list = []
show_list = []
failed_shows = []
name = ""
votes = 0
show_name = {}
show_vote = {}

def FileStuff(filein,fileout):
    try:
        fin = open(filein, "r")
        fout = codecs.open(fileout, 'w', 'utf-8')
        ftemp = codecs.open("temp.ha", 'w', 'utf-8')
    except IOError:
        print "Invalid file"

    files = [fin,fout,ftemp]
    return files


def ChooseOne(res,name,votes):
    option = 1
    if (len(res) < 1):
        print "Couldn't find show with : " + name.encode("latin_1", 'replace')
        return DiscoverInfo(raw_input("Please enter new search string: "),votes)
    for opt in res:
        print "Option " + str(option)
        print "   Title: " + opt['title'].encode("latin_1", 'replace')
        print "-------------------------------"
        option += 1

    choice = raw_input("Which one is correct for '" + name.encode("latin_1", 'replace') + "' (if not listed enter name to search): ")    

    try:
        dec = int(choice)
    except ValueError:
        return DiscoverInfo(choice,votes)

    while not((dec-1) in range(len(res))):
        choice = raw_input("Please enter valid option or new search: ")
        try:    
            dec = int(choice)
               except ValueError:
            return DiscoverInfo(choice,votes)


    return res[dec-1]


def DiscoverInfo(name,votes):
    information = []
    failures = 0
    url = "http://mal-api.com/anime/search?"
    req = urllib2.Request(url + urllib.urlencode({'q' : name}))
    opener = urllib2.build_opener()
    while (True):
        raw = opener.open(req)
        try:
            res = json.load(raw)
            break
        except ValueError:
            if (failures > 2):
                print " ---------ERROR-------- "
                print "skipping " + name.encode("latin_1", 'replace') + " because JSON get failed too many times"
                print "will attempt to continue with rest of file"
                failed_shows.append([name,votes])
                return "FAILED TO GET SHOW INFO"
            print "Didn't recieve valid JSON for url: " + url + name.encode("latin_1", 'replace')
            failures += 1
            #time.sleep(2)

    choice = ChooseOne(res,name,votes)
    print " "
    return choice #return top result


def ExistsInDict(id):
    if (id in show_name):
        return True
    else:
        return False


def AddToDict(result,show):
    id = str(result['id'])
    if (ExistsInDict(id)):
        print "Adding votes from " + show[0].encode("latin_1", 'replace') + " to " + show_name[id].encode("latin_1", 'replace')
        show_vote[id] += show[1]
        openfile[2].write(result['title'] + "," + str(show_vote[id]) + ",********\n")
    else:
        print "Adding new show " + result['title'].encode("latin_1", 'replace')
        show_name[id] = result['title']
        show_vote[id] = show[1]
        openfile[2].write(result['title'] + "," + str(show[1]) + "\n")


def PrintTheCSV():
    temp = []
    toPrint = []
    for i in show_name.iteritems():
        temp.append([show_name[i[0]],show_vote[i[0]]])
    sorted_list = sorted(temp, key=operator.itemgetter(1), reverse=True)
    for name,vote in sorted_list:
        openfile[1].write(name + "," + str(vote) + "\n")
        toPrint.append(name + "," + str(vote) + "\n")    


def PrintTheErrors(num):
    l = 0
    errors = []
    openfile[1].write("\n" + "-------FAILED-------" + "\n")
    openfile[1].write("The shows here encountered JSON errors when retrieving\n" + "\n")
    for show in failed_shows:
        if (l > num):
            break
        openfile[1].write(show[0] + "," + str(show[1]) + "\n")
        l += 1
    


openfile = FileStuff(filenamein,filenameout)
raw_list = openfile[0].readlines()

for entry in raw_list:
    ashow = []
    entry = entry.strip('\n')
    ashow = entry.split(',')
    ashow[1] = int(ashow[1])
    show_list.append(ashow)


for show in show_list:
    info = DiscoverInfo(show[0],show[1])
    if (info != "FAILED TO GET SHOW INFO"):
        AddToDict(info,show)

print "Trying failed shows"

length = len(failed_shows)

l = length

for show in failed_shows:
    if (l < 0):
        break
    l -= 1
    info = DiscoverInfo(show[0],show[1])
    if (info != "FAILED TO GET SHOW INFO"):
        AddToDict(info,show)
                
PrintTheCSV()
PrintTheErrors(length)

for f in openfile:
    f.close()

print "Script Complete"    