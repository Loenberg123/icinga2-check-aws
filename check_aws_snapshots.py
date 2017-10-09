#!/usr/bin/python
import boto3,os,sys,argparse,datetime,pytz

# Sensor que indica snapshots con mas del tiempo indicado
# Configurar fichero /etc/boto.cfg incluyendo las credenciales de aws de la siguiente forma
# [Credentials]
# aws_access_key_id =
# aws_secret_access_key =

# Definir argumentos para critical y warning, y mostrar ayuda en caso de no indicar argumentos
parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''Sensor que indica snapshots con mas del tiempo indicado

-----------------------------------------------------------------------------------------------------
IMPORTANTE: Configurar fichero /etc/boto.cfg incluyendo las credenciales de aws de la siguiente forma
[Credentials]
aws_access_key_id =
aws_secret_access_key =
-----------------------------------------------------------------------------------------------------''',
        epilog='Ejemplo de uso: check_aws_snapshots.py [-d] -n 32 -w 100 -c 200 -r eu-west-1'
)

parser.add_argument("-d", "--dias", help="Usar dias. Si no se indica se usan semanas", default="weeks", const="days", action="store_const")
parser.add_argument("-n", "--nmb", help="Indicar numero de dias/semanas")
parser.add_argument("-w", "--warn", help="Indica nivel de warning")
parser.add_argument("-c", "--crit", help="Indica nivel de critico")
parser.add_argument("-r", "--region", help="Indicar region de aws")

# Mostrar uso del comando si no se indican argumentos
if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)
args = parser.parse_args()

# Aviso en caso de no indicar region de aws
if not args.region:
    print('Especifique una region de aws con -r o --region')
    sys.exit(1)

# Aviso en caso de no indicar valor para dias/semanas
if args.region and not args.nmb:
    print('No se indico valor para -n')
    sys.exit(1)

# Aviso en caso de no indicar valores para warning y critico
if args.region and not args.warn or not args.crit:
    print('Indique valores para warning y critico con -w y -c')
    sys.exit(1)

# Definir cliente ec2
ec2 = boto3.client('ec2', region_name=args.region)

# Describir instancias que estan en estado running y almacenar en variable response
response = ec2.describe_snapshots()

# Obtener fecha actual offset-aware y almacenar en variable
now = pytz.utc.localize(datetime.datetime.utcnow())

# Pasar valor a int
n = int(args.nmb)
crit = int(args.crit)
warn = int(args.warn)
# Establecer el delta para comprobar diferencia de fecha
if args.dias == "weeks":
	delta = datetime.timedelta(weeks=n)
elif args.dias == "days":
	delta = datetime.timedelta(days=n)

# Iniciar variable para obtener el numero de snapshots
snaps = 0
ids = []
times = []

# Recorrer el diccionario JSON obtenido y obtener los diferentes valores de cada snapshot
for snapshot in response['Snapshots']:
	if (now - snapshot['StartTime']) >  delta:
		id = snapshot['SnapshotId']
		ids.append(id)
		time = snapshot['StartTime']
		times.append(time)
		snaps += 1

x = 0

# Mostrar el numero de snapshots con mas del tiempo indicado
if snaps >= warn and snaps < crit:
	print "WARNING - Existen "+str(snaps)+" snapshots con mas de "+str(delta.days)+" dias"
	while x < snaps:
		print "Id: "+ids[x]+" T: "+(str(times[x]))
		x += 1
	sys.exit(1)
elif snaps >= crit:
	print "CRITICAL - Existen "+str(snaps)+" snapshots con mas de "+str(delta.days)+" dias"
	while x < snaps:
		print "Id: "+ids[x]+" T: "+(str(times[x]))
		x += 1
	sys.exit(2)
elif snaps < warn:
	print "OK - Existen "+str(snaps)+" snapshots con mas de "+str(delta.days)+" dias"
	while x < snaps:
		print "Id: "+ids[x]+" T: "+(str(times[x]))
		x += 1
	sys.exit(0)
