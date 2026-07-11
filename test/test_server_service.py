from servers.services.server_config import get_server
from servers.services.server_service import ServerControlService


server = get_server("homestead")
service = ServerControlService(server)

status = service.get_status()

print("Server:", server.name)
print("Service:", server.service)
print("Active state:", status.active_state)
print("Sub-state:", status.sub_state)
print("Running:", status.is_running)