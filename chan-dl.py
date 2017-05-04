#!/usr/bin/env python3
import requests, re, os, time, signal, sys, argparse
tl = os.path.expanduser("~") + '/.threadlist'
parser = argparse.ArgumentParser(description='4chan thread image downloader.')
parser.add_argument('-a', '--add', help='Adds url to thread list.', nargs=1, action='store', dest='add', metavar='URL')
parser.add_argument('-d', '--delete',  help='Removes url from thread list.', nargs=1, action='store', dest='delete', metavar='URL')
parser.add_argument('-v', '--version', help='Prints version info.', action='store_true')
parser.add_argument('-s', '--start', help='Starts chan-dl on all the urls contained within the thread list.', action='store_true')
parser.add_argument('-p', '--prefix',  help='Prefix for the download directory.', nargs=1, action='store', dest='prefix', metavar='Directory', default=os.getcwd())
args = parser.parse_args()
reurl = re.compile('^https?://boards.4chan.org/([0-9a-z]+)/thread/([0-9]{7})$')
def signal_handler(signal, frame):
  print('Keyboard interrupt pressed: Exiting now.')
  sys.exit(2)
signal.signal(signal.SIGINT, signal_handler)
def get_file(url, filename):
  if not os.path.exists(filename):
    print('Downloading to {} ...'.format(filename))
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as fd:
      try:
        for chunk in r.iter_content(10240):
          fd.write(chunk)
      except:
        print('Requests exception... crashing and burning.')
        sys.exit(-1)
def delete(argurl, reurl):
  if not reurl.match(argurl):
    print('not a valid url')
    sys.exit(1)
  else:
    threadexists = False
    threadlist = open(tl, 'r+')
    threads = threadlist.readlines()
    threadlist.close()
    for thread in threads:
      if argurl in thread:
        threadexists = True
    if threadexists:
      open(tl ,'w').close()
      for thread in threads:
        if argurl not in thread:
          threadlist = open(tl, 'a')
          threadlist.write(thread)
          threadlist.close()
      print('Removed {} from thread list.'.format(argurl))
    else:
      print('Thread isn\'t already in thread list.')
      sys.exit(1)
if args.add:
  argurl = ''.join(args.add)
  if not reurl.match(argurl):
    print('not a valid url')
    sys.exit(1)
  else:
    threadlist = open(tl, 'r')
    threads = threadlist.readlines()
    threadlist.close()
    for thread in threads:
      if argurl in thread:
        print('Already watching thread.')
        sys.exit(0)
    threadlist = open(tl, 'a')
    threadlist.write(argurl + '\n')
    threadlist.close()
    print('Added {} to the thread list.'.format(argurl))
    sys.exit(0)
if args.delete:
  argurl = ''.join(args.delete)
  delete(argurl, reurl)
  sys.exit(0)
if args.version:
  print('Version 0.01 by snowfag Yuki@lolicon.eu')
  sys.exit(0)
if args.start:
  deleteurl = None
  while True:
    if deleteurl != None:
      delete(deleteurl, reurl)
      deleteurl = None
    else:
      threadlist = open(tl, 'r+')
      threads = threadlist.readlines()
      threadlist.close()
      for thread in threads:
        url = thread.strip()
        try:
          if requests.get('https://boards.4chan.org/').status_code != 200:
            print('Error connecting to 4chan... Waiting.')
            time.sleep(300)
        except:
          print('Error failed to check if 4chan is up.')
          time.sleep(300)
        else:
          try:
            print(url)
            if requests.get(url).status_code == 404:
              deleteurl = url
            else:
              reimg = re.compile('(?:https?:)?(?://)?(?:i.4cdn|is[0-9]?.4chan).org/[0-9a-z]+/([0-9]{13}\.(?:jpg|jpeg|gif|png|webm))')
              downdir = ''.join(args.prefix) + '/' + reurl.match(url).group(1) + reurl.match(url).group(2) + '/'
              if not os.path.exists(downdir):
                os.makedirs(downdir)
              imageurls = list(set(re.findall(r'(?:https?:)?(?://)?(?:i.4cdn|is[0-9]?.4chan).org/./[0-9]{13}\.(?:jpg|jpeg|gif|png|webm)', requests.get(url).text)))
              for imageurl in imageurls:
                imageurl = 'https:' + imageurl
                filename = downdir + reimg.match(imageurl).group(1)
                get_file(imageurl, filename)
          except:
            print('Error failed to check thread status.')
            time.sleep(300)
    time.sleep(600)
