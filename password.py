# ­*­ coding: utf­8 ­*­
import sys
import os
import MySQLdb

#usuario,servicio donde modificaremos y la nueva contraseña
usuario = sys.argv[1]
servicio = sys.argv[2]
newpasswd = sys.argv[3]

# Comprobamos que el usuario está registrado
if servicio == "ftp":
    if os.path.isdir("/var/www/%s" % (usuario)) == True:
#Abrimos la conexion con la base de datos del usuario
        conexion2 = MySQLdb.connect(host="localhost", user="root", passwd="root", db="ftpd")
        cursor2 = conexion2.cursor()
        changepass2 = "update usuarios set password = PASSWORD('%s')where username='%s';" % (newpasswd,usuario)
        cursor2.execute(changepass2)
        conexion2.commit()
        print "Password FTP actualizada correctamente."
    else:
        print "El usuario %s no existe, pruebe con un usuario existente." % (usuario)
        exit()
# Comprobamos que el usuario está registrado
elif servicio == "mysql":
    if os.path.isdir("/var/www/%s" % (usuario)) == True:
#Abrimos la conexion con la base de datos de mysql
        conexion = MySQLdb.connect(host="localhost", user="root", passwd="root", db="mysql")
        cursor = conexion.cursor()
        changepass = "set password for %s@localhost = PASSWORD('%s');" % (usuario,newpasswd)
        cursor.execute(changepass)
        conexion.commit()
        print "Password mysql actualizada correctamente."
    else:
        print "El usuario %s no existe, Pruebe con usuario existente." % (usuario)
        exit()
else:
        print "Se ha producido un error, parámetros: nombre de usuario, sistema: mysql o ftp y la nueva contraseña."
        print "Ejemplo: password.py usuario1 mysql passwordnueva"
