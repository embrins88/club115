from servers.services.comparison_service import ComparisonService
from servers.services.delete_service import DeleteService
from servers.services.server_config import get_server


server = get_server("homestead")
comparison = ComparisonService(server).run()

result = DeleteService(
    server,
    comparison,
    dry_run=True,
).run()

print("Files that would be deleted:")

for path in result.planned:
    print(f"  - {path}")

for error in result.errors:
    print(f"ERROR: {error}")