#!/usr/bin/python
import boto3,os,sys,argparse

# Sensor para ver si existen volumenes sin asignar al Tag Proyecto
# Configurar fichero /etc/boto.cfg incluyendo las credenciales de aws de la siguiente forma
# [Credentials]
# aws_access_key_id =
# aws_secret_access_key =

# Definir argumentos para critical y warning, y mostrar ayuda en caso de no indicar argumentos
parser = argparse.ArgumentParser(
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description='''Sensor que indica si existen volumenes sin asignar al tag proyectos en aws

-----------------------------------------------------------------------------------------------------
IMPORTANTE: Configurar fichero /etc/boto.cfg incluyendo las credenciales de aws de la siguiente forma
[Credentials]
aws_access_key_id =
aws_secret_access_key =
-----------------------------------------------------------------------------------------------------''',
	epilog='Ejemplo de uso: check_aws_volumes.py -w 100 -c 200 -r eu-west-1'
)

parser.add_argument("-w", "--warn", help="Indica nivel de warning")
parser.add_argument("-c", "--crit", help="Indica nivel de critico")
parser.add_argument("-r", "--region", help="Indicar region de aws")
if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)
args = parser.parse_args()

# Aviso en caso de no indicar region de aws
if not args.region:
    print('Especifique una region de aws con -r o --region')
    sys.exit(1)

# Aviso si no se indican los valores de critico y warning
if args.region and not args.warn or not args.crit:
    print('Indique valores para warning y critico con -w y -c')
    sys.exit(1)

# Se crea el cliente
ec2 = boto3.client('ec2', region_name=args.region)

# Describir volumenes de ec2 sin asignar al tag y se almacena en variable response
response = ec2.describe_volumes(Filters=[{'Name': 'tag:Proyecto','Values': ['Not tagged',],},],)

# Almacenamos el item Volumes de la respuesta en variable volumes
volumes = response['Volumes']

# Genera los diferentes estados
if len(volumes) >= int(args.warn) and len(volumes) < int(args.crit):
	print('WARNING - '+str(len(volumes))+' Volumenes sin asignar al tag: Proyecto')
        sys.exit(1)
elif len(volumes) >= int(args.crit):
	print('CRITICAL - '+str(len(volumes))+' Volumenes sin asignar al tag: Proyecto')
        sys.exit(2)
elif not volumes:
	print('OK - Ningun volumen sin asignar al tag: Proyecto')
        sys.exit(0)
else:
	print('UNKNOWN - No se pudieron obtener datos de Volumenes')
	sys.exit(3)
