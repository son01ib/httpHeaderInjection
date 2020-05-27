#Script used to get the http status code from a given domain/subdomain. Will put the 
#domain(s)/subdomian(s) in the respective file
#of the status code if a 2xx or 3xx is returned.

import httplib2
import os
import argparse
import sys

#check version of python used to run program
if sys.version_info[0] > 2:
    print("Please make sure you are using python 2.")
    sys.exit(0)

#build path if it doesn't exist
if not os.path.isdir("./statusCodes"):
    os.mkdir("./statusCodes")
#open necessary files
codes200 = open("./statusCodes/200CodesHTTP", "w")
codes300 = open("./statusCodes/300CodesHTTP", "w")
codes200HTTPS = open("./statusCodes/200CodesHTTPS", "w")
codes300HTTPS = open("./statusCodes/300CodesHTTPS", "w")
files = [codes200, codes300, codes200HTTPS, codes300HTTPS]

def closeFiles(filesOpen):
    for files in filesOpen:
        files.close()

def getStats(f200, f200HTTPS, f300, f300HTTPS, error):
    num_lines200 = sum(1 for line in f200)
    num_lines200HTTPS = sum(1 for line in f200HTTPS)
    num_lines300 = sum(1 for line in f300)
    num_lines300HTTPS = sum(1 for line in f300HTTPS)
    num_linesError = (sum(1 for line in error)/2)
    print("\n\nFinal count:\n" \
          "HTTP 2xx codes: {0}\n" \
          "HTTP 3xx codes: {1}\n" \
          "HTTPS 2xx codes: {2}\n" \
          "HTTPS 3xx codes: {3}\n\n" \
          "Total Errors: {4}".format(num_lines200, num_lines300, num_lines200HTTPS, \
          num_lines300HTTPS, num_linesError))

def checkStatus(proto, url, status):
    #check the first number of status code returned
    if status[0] == "2":
        if proto == "http://":
            codes200.write(url+"\n")
            print("Received http {} for ".format(status)+url)
        else:
            codes200HTTPS.write(url+"\n")
            print("Received https {} for ".format(status)+url)
    if status[0] == "3":
        if proto == "http://":
            codes300.write(url+"\n")
            print("Received http {} for ".format(status)+url)
        else:
            codes300HTTPS.write(url+"\n")
            print("Received https {} for ".format(status)+url)
    #other status codes we aren't interested in
    if status[0] == "1" or status[0] == "4" or status[0] == "5":
        print("Status code {} received for ".format(status)+url) 


def getResponse(proto, url):
    #use httplib2 to send request and get content back
    resp, content = httplib2.Http().request(url)
    #parse out content for http status code
    status = str(resp.status)
    #send to checkStatus to determine status code and which file
    #to write it to.
    checkStatus(proto, url, status)

def buildURL(proto, subdomains, iterate):
    if iterate == False:
        #strip domain of extra bytes
        subdomains = subdomains.rstrip("\n")
        #build url
        url  = proto+subdomains
        print("Trying "+url)
        try:
            getResponse(proto, url)
        except Exception as e:
            statusError = open("./statusCodes/statusErrors", "a")
            print(str(e)+"\n")
            statusError.write("Error for "+url+str(e))
            statusError.write("\n---------------------------------\n")
            statusError.close()
        print("----------------------------------")
    else:
        for subdomain in subdomains:
            #strip domain of extra bytes
            subdomain = subdomain.rstrip("\n")
            #build url
            url  = proto+subdomain
            print("Trying "+url)
            try:
                getResponse(proto, url)
            except KeyboardInterrupt:
                closeFiles(files)
                codes200 = open("./statusCodes/200CodesHTTP", "r")
                codes300 = open("./statusCodes/300CodesHTTP", "r")
                codes200HTTPS = open("./statusCodes/200CodesHTTPS", "r")
                codes300HTTPS = open("./statusCodes/300CodesHTTPS", "r")
                statusError = open("./statusCodes/statusErrors", "r")
                #get status to print out at the end
                getStats(codes200, codes200HTTPS, codes300, codes300HTTPS, statusError)
                sys.exit(0)
            except Exception as e:
                statusError = open("./statusCodes/statusErrors", "a")
                print(str(e)+"\n")
                statusError.write(str(e))
                statusError.write("\n---------------------------------\n")
                statusError.close()
            print("----------------------------------")
    #if statement here as subdomains can be a string and will throw
    #error if you try to close a string as opposed to file.
    if type(subdomains) == file:
        subdomains.close()


def main(proto, subdomains, iterate):
    #run program twice if both protos are to be checked
    if proto == "both":
        buildURL("http://", subdomains, iterate)
        buildURL("https://", subdomains, iterate)
    else:
        #run just once for the proto selected
        buildURL(proto, subdomains, iterate)
    #Need more efficient way to read files for the status func
    closeFiles(files)
    codes200 = open("./statusCodes/200CodesHTTP", "r")
    codes300 = open("./statusCodes/300CodesHTTP", "r")
    codes200HTTPS = open("./statusCodes/200CodesHTTPS", "r")
    codes300HTTPS = open("./statusCodes/300CodesHTTPS", "r")
    statusError = open("./statusCodes/statusErrors", "r")
    #get status to print out at the end
    getStats(codes200, codes200HTTPS, codes300, codes300HTTPS, statusError)
    #close open files
    closeFiles(files)

if __name__ == "__main__":
    #parse input
    parser = argparse.ArgumentParser(description='Program to obtain' \
                                    ' status code of given domain(s)/subdomain(s).')
    parser.add_argument('-f', '--file', metavar='', help='File containing' \
                                                    ' domains or subdomains' \
                                                    ' to test.')
    parser.add_argument('-s', '--single', metavar='', help='Single domain or' \
                                                    ' subdomain to test.')
    args = parser.parse_args()

    if args.file is None and args.single is None:
        print("No domains supplied. Use --help for help.")
        sys.exit(1)
    if args.file is not None:
        d = open(args.file, "r")
        iterate = True
    else:
        d = args.single
        iterate = False
        

    option = raw_input("Which protocol do you want to use?\n" \
                        "\t1. http\n" \
                        "\t2. https\n" \
                        "\t3. both\n" \
                        ":")
    if option == "1":
        proto = "http://"
    if option == "2":
        proto = "https://"
    if option == "3":
        proto = "both"
    #The line below was put in as a check but for some reason, when it is
    #uncommented, 1 and 2 will print invalid input and only 3 will work.
    #else:
    #    print("\nInvalid input")
    #    sys.exit(1)

    main(proto, d, iterate)
