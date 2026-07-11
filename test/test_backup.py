from servers.services.checkpoint_service import BackupService
from servers.services.server_config import get_server


server = get_server("homestead")
service = BackupService(server)

backup_path = service.run()

print("Backup created:")
print(backup_path)