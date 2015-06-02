# -*- coding: utf-8 -*- 
import os
import sys
import MySQLdb

#creamos un objeto con las opciones
dominio=sys.argv[1]

### MySQL
## Conectamos con la base de datos con MySQLdb
conexion = MySQLdb.connect(host="localhost",user="root",passwd="root",db="ftpd")
cursor = conexion.cursor()

#Para comprobar que el usuario existe haremos una consulta a la base de datos
consulta = "select username from usuarios where dominio='%s';" % (dominio)
cursor.execute(consulta)
usuario = cursor.fetchone()
if usuario == None:
    print "Lo sentimos, el dominio %s no existe" % (dominio)
#si obtenemos usuario seguira el programa seguirá ejecutandose
else:
## Borramos al usuario en el servicio mysql
    borrarbd = "drop database %s;" % (usuario)
    cursor.execute(borrarbd)
    conexion.commit()


## Borramos al usuario 
    borrarusuario = "drop user %s@localhost;" % (usuario)
    cursor.execute(borrarusuario)
    conexion.commit()


### PROFTP
## Vamos a eliminar al usuario del servicio FTP, para ello eliminamos de la tabla usuarios.
    borrarftpuser = "delete from usuarios where dominio='%s';"% (dominio)
    cursor.execute(borrarftpuser)
    conexion.commit()
    conexion.close()

### Apache
## Borramos todos los directorios creados para el usuario
    os.system("rm -r /var/www/%s" % (usuario))
    os.system("a2dissite %s > /dev/null" % (usuario))
    os.system("a2dissite phpmyadmin%s > /dev/null" % (usuario))
    os.system("rm /etc/apache2/sites-available/%s" % (usuario))
    os.system("service apache2 restart > /dev/null")
    os.system("rm /etc/apache2/sites-available/phpmyadmin%s" % (usuario))


### DNS
## Eliminamos lineas de named.local
    os.system("rm /var/cache/bind/db.%s" % (dominio))

## Eliminamos los ficheros del usuario
    os.system("sed '/zone " + '"%s"'% (dominio) + "/,/};/d' /etc/bind/named.conf.local > temporal")
    os.system("mv temporal /etc/bind/named.conf.local")
    print "El usuario %s y el dominio %s han sido eliminados" % (usuario,dominio)

