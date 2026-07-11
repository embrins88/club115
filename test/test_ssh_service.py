from servers.services.server_config import get_server
from servers.services.ssh_service import SSHService


server = get_server("homestead")
ssh = SSHService(server)

result = ssh.run("hostname")

print("Server:", server.name)
print("Exit code:", result.exit_code)
print("Hostname:", result.stdout)
print("Succeeded:", result.succeeded)