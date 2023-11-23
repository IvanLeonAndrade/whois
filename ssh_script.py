import paramiko
import sys
import re

# Busca un patrón que corresponda a una dirección IP después de la palabra 'from'
def find_next_hop(output):
    match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', output)
    if match:
        return match.group(1)  # Devuelve la dirección IP encontrada
    return None

def find_sub_interface(output):
    # Busca un patrón que corresponda a una subinterfaz después de la palabra 'via', excluyendo 'ae0.0'
    matches = re.findall(r'via ((?!ae0\.0)\S+)', output)
    for match in matches:
        if match != 'ae0.0':  # Asegúrate de que no sea 'ae0.0'
            return match
    return None

def find_sub_interface_vlan(subinterface):
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

def find_relevant_hop(output, search_ip):
    # Descomponer la IP de búsqueda en sus primeros tres segmentos
    search_segments = '.'.join(search_ip.split('.')[:3])

    # Buscar en la salida del comando una entrada que coincida con esos segmentos
    pattern = re.compile(rf'{search_segments}\.\d+/\d+.*?from (\d+\.\d+\.\d+\.\d+)', re.DOTALL)
    match = pattern.search(output)

    if match:
        return match.group(1)  # Devuelve la dirección IP encontrada después de 'from'
    return None
    

def execute_ssh_command(host, command):
    username = 'iandrade'
    password = 'transistor13'
    port = 22
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



if __name__ == "__main__":
    host = '186.0.255.32' # PE Cualquiera
    ip_analizer = '200.61.16.80'
    command_route = 'show route '
    command_route += ip_analizer
    print(command_route)
    
    command_configuration = 'show configuration | display set | match ' 
    host_nex_hop = None
    id_service = None
    sub_interface = None
    sub_interface_vlan = None
    
    # primer show route en PE X
    output, error = execute_ssh_command(host, command_route)
    print(output)
    

    # Segundo show route donde aprendo la IP
    host_nex_hop = find_relevant_hop(output, ip_analizer)
    print(host_nex_hop)
    sys.exit()

    # Obtengo la sub IF del cliente que usa la IP
    output, error = execute_ssh_command(host_nex_hop, command_route)
    print(output)
    sub_interface = find_sub_interface(output)

    # Obtengo la vlan de la sub IF
    sub_interface_vlan = find_sub_interface_vlan(sub_interface)

    # Configuracion machiando x la vlan
    command_configuration += sub_interface_vlan
    print(command_configuration)

    output, error = execute_ssh_command(host_nex_hop, command_configuration)
    print(output)

    # Obtengo el ID de servicio
    id_service = find_id_service(output)
    print('nex-hop: ', host_nex_hop)
    print('sub IF: ', sub_interface)
    print('sub IF vlan: ', sub_interface_vlan)
    print('IUS', id_service)

if error:    
    print("Error:", error)
