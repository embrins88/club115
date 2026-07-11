from servers.services.comparison_service import ComparisonService
from servers.services.server_config import get_server


server = get_server("homestead")
service = ComparisonService(server)
result = service.run()

print(f"Server: {result.server_name}")
print(f"Added: {len(result.added)}")
print(f"Updated: {len(result.updated)}")
print(f"Removed: {len(result.removed)}")
print(f"Total changes: {result.total_changes}")

if result.skipped_directories:
    print("\nMissing local directories:")
    for directory in result.skipped_directories:
        print(f"  - {directory}")

if result.added:
    print("\nAdded:")
    for change in result.added:
        print(f"  + {change.path}")

if result.updated:
    print("\nUpdated:")
    for change in result.updated:
        print(f"  ~ {change.path}")

if result.removed:
    print("\nRemoved:")
    for change in result.removed:
        print(f"  - {change.path}")

if result.errors:
    print("\nErrors:")
    for error in result.errors:
        print(f"  ! {error}")