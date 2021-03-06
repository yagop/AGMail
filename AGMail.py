#!/usr/bin/python
# -*- coding: utf-8 -*-

import cookielib
import urllib, urllib2
import sys, os
import argparse
from bs4 import BeautifulSoup
import re
import getpass

courses = []
alumnos = []
roleid = '8' #Default role for students
emails = []
todos = False

class Course:
	def __init__(self, name, link, number):
		self.name = name
		self.link = link
		self.number = number

def process_main(html):
	global courses
	cont = BeautifulSoup(html)

	busqueda = cont.find("div", {"id": "miscursosp"})

	if busqueda == None:
		print "No courses found. ¿Login error?"
		exit()

	find = busqueda.find_all('a')[1:] # LOL clean this also

	for line in find:
		#TODO clean this code
		# First is NoneType 
		link = line.get('href')
		name = line.get_text()
		number = re.search("\d+$",link).group()
		# Filter 
		if re.search("course/view.php", link):
			course = Course(name, link, number)
			courses.append(course)

def ask_user():
	yes = set(['si','s', ''])
	no = set(['no','n'])

	choice = raw_input().lower()
	if choice in yes:
	   return True
	elif choice in no:
	   return False
	else:
	   sys.stdout.write("Por favor, responde 'si' o 'no'") 

def process_courses(opener):
	global courses
	global mfiles
	for curso in courses:

		if not todos:
			print ("Desea anadir los alumnos de "+curso.name+"? [S/n]") #La interrogacion primera da problemas 
			answer = ask_user()
		else:
			print ("Analizando "+curso.name)
			answer = True 

		if answer:
			fullurl='https://aulaglobal.uc3m.es/user/index.php?roleid='+roleid+'&id='+curso.number+'&mode=1&search=&perpage=5000'
			resp = urllib2.urlopen(urllib2.Request(fullurl))
			contents = resp.read()

			emails_f = re.findall(r'[\w\.-]+@[\w\.-]+', contents) 
	   
			for email in emails_f:
				if email not in emails:
					emails.append(email)


def process_emails():
	print 'Se han econtrado '+str(len(emails))+' emails no repetidos'
	print ', '.join(emails)
	print ("Desea guardarlos en emails.txt ? [S/n]")
	if ask_user():
		f = open('emails.txt', 'w')
		for email in emails:
  			f.write("%s, " % email)

def login_moodle (user, passwd, opener):
	
	# http://stackoverflow.com/questions/13925983/login-to-website-using-urllib2-python-2-7
	opener.addheaders = [('User-agent', ' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0')]
	urllib2.install_opener(opener)
	authentication_url = 'https://aulaglobal.uc3m.es/login/index.php'
	
	payload = {'username': user, 'password': passwd }
	  
	data = urllib.urlencode(payload)
	req = urllib2.Request(authentication_url, data)
	resp = urllib2.urlopen(req)
	contents = resp.read()
	
	return contents
   
def main():
	parser = argparse.ArgumentParser(description='AGMail')
	parser.add_argument("-all", "--all", help="Analiza todos los cursos sin preguntar", action="store_true")
	args = parser.parse_args()

	if args.all == True:
		global todos
		todos = True

	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

	print "Introduce tu usuario (NIA)"
	nia = sys.stdin.readline().rstrip("\n")

	print "Introduce tu contraseña"
	password = getpass.getpass()

	cont = login_moodle(nia, password, opener)
	process_main(cont)
	process_courses(opener)
	process_emails()
	
#TODO clean this
if __name__ == '__main__':
        try:
            main()
        except KeyboardInterrupt:
            pass
