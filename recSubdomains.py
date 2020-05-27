#Script to get subdomains of given domain(s). Uses the site https://crt.sh/?q=<insert domain>
#to get the subdomains and removes any duplicates.

import requests
import argparse
import sys
import os

def parseData(data, domain, response):
    #tried passing the tmpSubs file object in parameters
    #but this is the only way I could get anything to write
    #to tmpSubs
    tmpSubs = open("./subDomResults/tmpSubs.txt", "a+")
    domain = domain.rstrip("\n")
    print("parsing data")
    read = open("./subDomResults/response.txt", "r")
    for line in read:
        #response from site contains extra data with domain
        #in the line. Below is to filter out those lines.
        if "TITLE" in line:
            continue 
        if "href" in line:
            continue
        if "&nbsp" in line:
            continue
        if "*" in line:
            continue
        #write the remaining lines that contain the url
        #without the extra html tags
        elif domain in line:
            a = line.replace('<TD>','')
            b = a.replace('</TD>','')
            c = b.replace('<BR>','\n')
            d = c.replace(' ','')
            tmpSubs.write(d)
    print("----------------------------------")

def getAndParse(domain):
        print("getting subdomains for "+domain.rstrip("\n"))
        #site that displays subdomains
        url = "https://crt.sh/?q=" + domain
        #strip the url before sending to remove \n in request
        url = url.rstrip("\n")
        try:
            #send get request to url above
            r = requests.get(url)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            #log any domains that cause any errors 
            f = open("./subDomResults/error.txt", "a+")
            f.write(str(domain)+"\n")
            f.write(str(e))
            f.write("----------------------------------"+"\n")
            print("Error occured with domain: "+str(domain))
            pass
        data = r.text
        #some urls were found to have unicode hence the encoding
        response.write(data.encode('utf-8'))
        domain = domain.rstrip("\n")
        parseData(data, domain, response)

def getSubdomains(domains, status):
    global counter
    counter=0
    if status == True:
        getAndParse(domains)
    else:
        for domain in domains:
            counter+=1
            getAndParse(domain)
        f.close()
    response.close()
    os.remove("./subDomResults/response.txt")

def rmDuplicates(tmpSubs):
    subdList = list(tmpSubs)
    tmpList = []
    print("\nSearching for duplicates")
    i=0
    for elem in subdList:
        i+=1
        print("\rProcessing element: {0}".format(i)+" of {0}".format(len(subdList))),
        if elem not in tmpList:
            tmpList.append(elem)
    print("\nWriting to subdomain.txt without duplicates")
    j=0
    for elem in tmpList:
        j+=1
        print("\rWriting element: {0}".format(j)+" of {0}".format(len(tmpList))),
        subdomains.write(elem)
    print("\nProcessed and wrote "+str(j)+" elements removing "+str(i-j)+" duplicates.")
    subdomains.close()
    tmpSubs.close()
    os.remove("./subDomResults/tmpSubs.txt")

def total(counter):
    f = open("./subDomResults/subdomains.txt")
    num_lines = sum(1 for line in f)
    print("\n\nReceived subdomains from "+str(counter)+" domains for a total of " \
            +str(num_lines)+" unique subdomains.\n")
    f.close()

def main(domains, tmpSubs, status):
    getSubdomains(domains, status)
    rmDuplicates(tmpSubs)
    total(counter)

if __name__ == "__main__":
    if sys.version_info[0] > 2:
        print("Please make sure you are using python 2.")
        sys.exit(0)
    if not os.path.isdir("subDomResults"):
        os.makedirs("subDomResults")

    tmpSubs = open("./subDomResults/tmpSubs.txt", "w+")
    subdomains = open("./subDomResults/subdomains.txt", "w+")
    response = open("./subDomResults/response.txt", "w+")

    parser = argparse.ArgumentParser(description='Program to obtain a list' \
                                       ' of subdomains for a given domain.' \
                                       ' Results written to' \
                                       ' ./subDomResults/subdomains.txt')
    parser.add_argument('-f', '--file', metavar='',
                    help='File with list of domains.')
    parser.add_argument('-d', '--domain', metavar='',
                    help='Single domain to get subdomains of.')
    args = parser.parse_args()    

    if args.domain is not None:
        f = args.domain
        status = True
    elif args.file is not None:
        f = open(args.file, "r")
        status = False
    else:
        print("No file or domain supplied.")
        sys.exit(1)
    main(f, tmpSubs, status)
