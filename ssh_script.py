import paramiko
import re


def find_next_hop(output):
    # Busca un patrón que corresponda a una dirección IP después de la palabra 'from'
    match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', output)
    if match:
        return match.group(1)  # Devuelve la dirección IP encontrada
    return None

def find_client_subinterface(output):
    # Busca un patrón que corresponda a una subinterfaz después de la palabra 'via', excluyendo 'ae0.0'
    matches = re.findall(r'via ((?!ae0\.0)\S+)', output)
    for match in matches:
        if match != 'ae0.0':  # Asegúrate de que no sea 'ae0.0'
            return match
    return None

def find_subinterface_vlan(subinterface):
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

    host = '186.0.255.53' # PE Cualquiera
    command = 'show route 186.0.196.225'
    ip_from = None #IP del PE donde se aprende la IP a analizar

    host2 = None
    id_service = None

    # Me conecto al PE con IP 186.0.255.32 y  ejecuto el primer command
    output, error = execute_ssh_command(host, command)
    sub_interface = find_client_subinterface(output)

    if "*[BGP/170]" in output and "via ae0.0," in output:
        # La ruta se aprende a través de otro router, buscar el siguiente hop
        ip_from = find_next_hop(output)
        if ip_from:
            print("Aprendo IP: ", ip_from)
            host2 = ip_from
            output, error = execute_ssh_command(host2, command)
            sub_interface = find_client_subinterface(output)
            print("sub if: ", sub_interface)
            if sub_interface:
                sub_interface_vlan = find_subinterface_vlan(sub_interface)
                command2 = 'show configuration | display set | match {}'.format(sub_interface_vlan)
                output, error = execute_ssh_command(host2, command2)
                id_service = find_id_service(output)
                print("IUS: ", id_service)
            else:
                print("No se encontró la subinterfaz adecuada.")
        else:
            print("No se encontró el siguiente hop.")
            host2 = ip_from
            output, error = execute_ssh_command(host2, command)
            sub_interface = find_client_subinterface(output)
            if sub_interface:
                sub_interface_vlan = find_subinterface_vlan(sub_interface)
                # Procesar la VLAN como necesites
                # ...
            else:
                print("No se encontró la subinterfaz adecuada.")
    else:
        # La ruta no se aprende a través de ae0.0, se maneja localmente
        if sub_interface:
            sub_interface_vlan = find_subinterface_vlan(sub_interface)
            sub_interface_vlan = find_subinterface_vlan(sub_interface)
            command2 = 'show configuration | display set | match {}'.format(sub_interface_vlan)
            output, error = execute_ssh_command(host, command2)
            id_service = find_id_service(output)
        else:
            print("No se encontró la subinterfaz adecuada.")





if error:    
    print("Error:", error)
