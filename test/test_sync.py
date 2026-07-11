from servers.services.server_config import get_server
from servers.services.sync_service import SyncService


server = get_server("homestead")
service = SyncService(server)
result = service.run()

print(f"Server: {result.server_name}")
print(f"Succeeded: {result.succeeded}")

for message in result.messages:
    print(message)

for error in result.errors:
    print(f"ERROR: {error}")