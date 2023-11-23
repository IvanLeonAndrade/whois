import paramiko
import re


def find_next_hop(output):
    # Busca un patrón que corresponda a una dirección IP después de la palabra 'from'
    match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', output)
    if match:
        return match.group(1)  # Devuelve la dirección IP encontrada
    return None

def find_subinterface(output):
    # Busca un patrón que corresponda a una subinterfaz después de la palabra 'via', excluyendo 'ae0.0'
    matches = re.findall(r'via ((?!ae0\.0)\S+)', output)
    for match in matches:
        if match != 'ae0.0':  # Asegúrate de que no sea 'ae0.0'
            return match
    return None

def find_subinterface_number(subinterface):
    # Busca un patrón que corresponda a los números después del punto en la subinterfaz
    match = re.search(r'\.(\d+)', subinterface)
    if match:
        return match.group(1)  # Devuelve solo los números después del punto
    return None

def find_id_service(output):
    match = re.search(r'description (.+)$', output, re.MULTILINE)

    if match:
        description_line = match.group(1)
        return description_line 
    

def execute_ssh_command(host, port, username, password, command):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port, username, password)

    # Ejecutar el comando principal
    stdin, stdout, stderr = client.exec_command(command)

    # Asegurarse de obtener toda la salida
    stdout.channel.recv_exit_status()

    output = stdout.read().decode()
    error = stderr.read().decode()
    client.close()

    return output, error

    return output, error

if __name__ == "__main__":

    host = '186.0.255.32' # Elijo cualquier PE
    port = 22
    username = 'iandrade'
    password = 'transistor13'
    #command = 'show route 186.0.196.225' # IP a analizar
    command = 'show route 200.59.198.196'
    ip_from = None #IP del PE donde aprende la IP a analizar
    host2 = None
    id_service = None

    # Me conecto al PE con IP 186.0.255.32 y  ejecuto el primer command
    output, error = execute_ssh_command(host, port, username, password, command)
    #print(output)
    
    # El resultado anterior lo filtro para tener la IP del PE donde aprendo la IP del comando principal
    ip_from = find_next_hop(output)


    # Ahora me conecto al PE con la IP de ip_from
    host2 = ip_from # Elijo cualquier PE
    output, error = execute_ssh_command(host2, port, username, password, command)
    sub_interface = find_subinterface(output)
    sub_interface_vlan = find_subinterface_number(sub_interface)
   

    # ahora veo la config de esa vlan en el PE principal 
    command2 = 'show configuration | display set | match {}'.format(sub_interface_vlan)
    #print('comando 2', command2)
    output, error = execute_ssh_command(host2, port, username, password, command2)
    #print(output)
    id_service = find_id_service(output)

    print("IP FROM: ", ip_from)
    print("SUB IF ", sub_interface)
    print("SUB IF VLAN ", sub_interface_vlan)
    print('IUS: ', id_service)





    if error:
        print("Error:", error)
