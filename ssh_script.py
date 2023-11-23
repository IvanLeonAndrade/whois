import paramiko
import sys
import re

# Busca un patrón que corresponda a una dirección IP después de la palabra 'from'
def find_relevant_hop(output, search_ip):
    # Descomponer la IP de búsqueda en sus primeros tres segmentos
    search_segments = '.'.join(search_ip.split('.')[:3])

    # Buscar en la salida del comando una entrada que coincida con esos segmentos
    # y verificar si hay una cláusula 'from'
    pattern = re.compile(rf'{search_segments}\.\d+/\d+.*?\n')
    match = pattern.search(output)

    if match:
        if 'from' in match.group(0):
            # Extrae la dirección IP después de 'from'
            from_ip = re.search(r'from (\d+\.\d+\.\d+\.\d+)', match.group(0))
            if from_ip:
                return from_ip.group(1)  # Devuelve la dirección IP encontrada después de 'from'
        else:
            # No hay cláusula 'from', asumir que es el mismo equipo
            return None
    return None


def find_relevant_sub_interface(output, search_ip):
    # Descomponer la IP de búsqueda en sus primeros tres segmentos
    search_segments = '.'.join(search_ip.split('.')[:3])

    # Buscar en la salida del comando una entrada que coincida con esos segmentos
    pattern = re.compile(rf'{search_segments}\.\d+/\d+\s+\*\[Direct.*?via (\S+)', re.DOTALL)
    match = pattern.search(output)

    if match:
        return match.group(1)  # Devuelve la subinterfaz encontrada después de 'via'
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
    host = '186.0.255.41' 
    ip_analizer = '200.61.16.80'
    command_route = 'show route '
    command_route += ip_analizer
    command_configuration = 'show configuration | display set | match ' 
    host_nex_hop = None
    id_service = None
    sub_interface = None
    sub_interface_vlan = None
    
    # primer show route en PE X
    output, error = execute_ssh_command(host, command_route)
    # Segundo show route donde aprendo la IP
    host_nex_hop = find_relevant_hop(output, ip_analizer)
    search_segments = '.'.join(ip_analizer.split('.')[:3])

    if (not host_nex_hop) and (search_segments in output):
        # La IP objetivo es manejada localmente
        output, error = execute_ssh_command(host, command_route)
        sub_interface = find_relevant_sub_interface(output, ip_analizer)
        sub_interface_vlan = find_sub_interface_vlan(sub_interface)

        command_configuration += sub_interface_vlan
        output, error = execute_ssh_command(host, command_configuration)
        id_service = find_id_service(output)
    
    else:
        # La IP objetivo es manejada remotamente
        output, error = execute_ssh_command(host_nex_hop, command_route)
        sub_interface = find_relevant_sub_interface(output, ip_analizer)
        sub_interface_vlan = find_sub_interface_vlan(sub_interface)

        command_configuration += sub_interface_vlan
        output, error = execute_ssh_command(host_nex_hop, command_configuration)
        id_service = find_id_service(output)

    print('host_nex_hop: ', host_nex_hop)
    print('sub_interface', sub_interface)
    print('sub_interface_vlan: ', sub_interface_vlan)
    print('IUS: ', id_service)
    
if error:    
    print("Error:", error)
