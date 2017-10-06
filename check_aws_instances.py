#!/usr/bin/python
import boto3,os,sys,argparse,datetime,pytz

# Sensor que indica instancias corriendo durante mas del tiempo indicado
# Configurar fichero /etc/boto.cfg incluyendo las credenciales de aws de la siguiente forma
# [Credentials]
# aws_access_key_id =
# aws_secret_access_key =

# Definir argumentos para critical y warning, y mostrar ayuda en caso de no indicar argumentos
parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''Sensor que indica instancias corriendo durante mas del tiempo indicado

-----------------------------------------------------------------------------------------------------
IMPORTANTE: Configurar fichero /etc/boto.cfg incluyendo las credenciales de aws de la siguiente forma
[Credentials]
aws_access_key_id =
aws_secret_access_key =
-----------------------------------------------------------------------------------------------------''',
        epilog='Ejemplo de uso: check_aws_instances.py [-d] [-e fichero_exclusion] -n 32 -w 100 -c 200 -r eu-west-1'
)

parser.add_argument("-e", "--exclude", help="Indicar fichero de exclusion")
parser.add_argument("-d", "--dias", help="Usar dias. Si no se indica se usan semanas", default="weeks", const="days", action="store_const")
parser.add_argument("-n", "--nmb", help="Indicar numero de dias/semanas")
parser.add_argument("-w", "--warn", help="Indica nivel de warning")
parser.add_argument("-c", "--crit", help="Indica nivel de critico")
parser.add_argument("-r", "--region", help="Indicar region de aws")

# Mostrar uso del comando si no se indican argumentos
if len(sys.argv)==1:
    parser.print_help()
    sys.exit(5)
args = parser.parse_args()

# Aviso en caso de no indicar region de aws
if not args.region:
    print('Especifique una region de aws con -r o --region')
    sys.exit(5)

# Aviso en caso de no indicar valor para dias/semanas
if args.region and not args.nmb:
    print('No se indico valor para -n')
    sys.exit(5)

if args.region and not args.warn or not args.crit:
    print('Indique valores para warning y critico con -w y -c')
    sys.exit(5)

# Definir cliente ec2
ec2 = boto3.client('ec2')

# Describir instancias que estan en estado running y almacenar en variable response
response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

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

# Iniciar variable para obtener el numero de instancias corriendo
inst = 0
top = []

# Leer fichero de exclusion y almacenar valores en lista si se indica su uso
list = []
if args.exclude is not None:
	excluir = open(args.exclude)
	for line in excluir:
	        line = line.strip('\n')
	        list.append(line)
	excluir.close()

# Recorrer el diccionario JSON obtenido y mostrar los diferentes valores de cada instancia
for reservation in response['Reservations']:
	for instance in reservation['Instances']:
		if (now - instance['LaunchTime']) > delta and instance['Tags'][0]['Value'] not in list:
			inst += 1
			top += [int(str((now - instance['LaunchTime']).days))]

# Mostrar el numero de instnacias corriendo durante mas del tiempo indicado
if inst >= warn and inst < crit:
	print 'WARNING - Hay '+str(inst)+' instancias que llevan mas de '+str(delta.days)+' dias funcionando | El mayor tiempo es '+str(max(top))+' dias'
	sys.exit(1)
elif inst >= crit:
	print 'CRITICAL - Hay '+str(inst)+' instancias que llevan mas de '+str(delta.days)+' dias funcionando | El mayor tiempo es '+str(max(top))+' dias'
	sys.exit(2)
elif inst < warn:
	print 'OK - Hay '+str(inst)+' instancias que llevan mas de '+str(delta.days)+' dias funcionando | El mayor tiempo es '+str(max(top))+' dias'
	sys.exit(0)
