# -*- coding: utf-8 -*- 
import os
import sys
import string
from random import choice
#creamos un objeto con las opciones
usuario=(sys.argv[1])
dominio=(sys.argv[2])

#importamos también el módulo de MySQL
import MySQLdb

if os.path.isdir("/var/www/%s" % (usuario)) == False and os.path.isfile("/etc/apache2/sites-available/%s" % (dominio)) == False:
	os.system("mkdir /var/www/%s" % (usuario))
else:
	print "El usuario: %s o el dominio: %s ya existen, Elija otro usuario o nombre de dominio" % (usuario,dominio)
	exit()


#### Creacion del espacio del usuario en APACHE
os.system("echo Home Page %s is being Build  > /var/www/%s/index.html" %(usuario,usuario))
# abriremos el fichero en modo lectura para poder diseñar el nuevo virtualhost 
virtualhost=open("plantillas/apache","r")
lista=virtualhost.read()
virtualhost.close()
#usamos el metodo replace para poder remplazar al nuevo usuario en el modelo para el virtualhost 
lista=lista.replace("@servername@","www.%s.com" % usuario)
lista=lista.replace("@mail@","%s@gmail.com"% usuario)
lista=lista.replace("@usuario@","%s"% usuario)
#abrimos el modo escritura y nos guarda el fichero del virtualhost creado para el usuario 
virtualhost=open("/etc/apache2/sites-available/%s" % usuario,"w")
virtualhost.write(lista)
virtualhost.close()
# activamos el nuevo sitio para el usuario
os.system("a2ensite %s >/dev/null" % usuario)
# Abrimos en modo lectura el modelo diseñado en el fichero php para que el usuario disponga de su phpmyadmin y pueda gestionar sus tablas,etc
phpmyadmin= open("plantillas/php","r")
lista2=phpmyadmin.read()
phpmyadmin.close()
lista2=lista2.replace("@servername@","%s.com" % usuario)
lista2=lista2.replace("@usuario@","%s"% usuario)
phpmyadmin=open("/etc/apache2/sites-available/phpmyadmin%s" % usuario,"w")
phpmyadmin.write(lista2)
phpmyadmin.close()
# Activamos el sitio phpmyadmin para el usuario
os.system("a2ensite phpmyadmin%s >/dev/null" % usuario)
# Reiniciamos apache
os.system("service apache2 restart >/dev/null ")



### Configuración de DNS
#abrimos la plantilla de la zona directa
fzonedir=open("plantillas/zonedirect","r")
#abrimos la plantilla para registrar el dominio
fzonedom=open("plantillas/zonedom","r")
lista=fzonedir.read()
lista2=fzonedom.read()
fzonedir.close()
fzonedom.close()
#reemplazamos en el fichero el dominio
lista2=lista2.replace("@dominio@","%s" % dominio)
#abrimos el fichero con el parametro a o sea modo añadir al final del documento
fzonedom=open("/etc/bind/named.conf.local","a")
fzonedom.write(lista2)
fzonedom.close()
#reemplazamos en el fichero dominio para guardarlo como un nuevo dominio y reiniciamos el servicio bind9
lista=lista.replace("@dominio@","%s" % dominio)
fzonedir=open("/var/cache/bind/db.%s" % (dominio),"w")
fzonedir.write(lista)
fzonedir.close()
os.system("service bind9 restart>/dev/null")



### MySQL configuración para el usuario generando passwd
#Generamos password para mysql
def GenPasswd(n):
        return ''.join([choice(string.letters + string.digits) for i in range(n)])
passwdmysql = GenPasswd(8)
#Generamos password para ftp
def GenPasswd(n):
        return ''.join([choice(string.letters + string.digits) for i in range(n)])
passwdftp = GenPasswd(8)
conexionbd = MySQLdb.connect(host="localhost", user="root", passwd="root", db="ftpd")
cursor = conexionbd.cursor()
print "La contraseña de MySQL para el usuario %s es %s" % (usuario,passwdmysql)
#creamos la base de datos para el usuario 
bdusuario="create database %s" % (usuario)
cursor.execute(bdusuario)
#creamos el usuario y le damos todos los permisos sobre la base de datos que creamos  antes
privilegessql= "grant all privileges on %s.* to"% (usuario)+ " %s@localhost"% (usuario)+ " identified by "+"'%s'" % (passwdmysql)
cursor.execute(privilegessql)
#guardamos los cambios
dbreload = "FLUSH PRIVILEGES;"
cursor.execute(dbreload)

### Configuración PROFTPD 
uid="select max(uid) from usuarios;"
cursor.execute(uid)
consultauid = cursor.fetchone()
if consultauid[0] == None:
	countuid=str(5001)
        insertuser=" INSERT INTO usuarios VALUES ('"+usuario+"',"+"PASSWORD('"+passwdftp+"'),"+countuid+","+countuid+","+"'/var/www/"+usuario+"',"+"'/bin/false',"+"1,'"+dominio+ "');"
	cursor.execute(insertuser)
	conexionbd.commit()
	os.system("chown -R %s:%s /var/www/%s" % (countuid,countuid,usuario))
else:
	countuid=consultauid[0]+1
	countuidin=str(countuid)
	insertuser=" INSERT INTO usuarios VALUES ('"+usuario+"',"+"PASSWORD('"+passwdftp+"'),"+countuidin+","+countuidin+","+"'/var/www/"+usuario+"',"+"'/bin/false',"+"1,'"+dominio+ "');"
        cursor.execute(insertuser)
	conexionbd.commit()
#Cambiamos el propietario de la carpeta creada en /var/www para cada usuario
	os.system("chown -R %s:%s /var/www/%s" % (countuidin,countuidin,usuario))
        print "La contraseña FTP para el usuario %s es %s" % (usuario,passwdftp)
print "El proceso se realizo satisfactoriamente"
