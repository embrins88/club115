from servers.services.sync_service import SyncService


service = SyncService()
result = service.preview("homestead")

print("Server:", result.server_name)
print("Dry run:", result.dry_run)
print("Succeeded:", result.succeeded)
print("Steps:", result.completed_steps)

if result.comparison:
    print("Changes:", result.comparison.total_changes)

if result.upload:
    print("Would upload:", len(result.upload.planned))

if result.deletion:
    print("Would delete:", len(result.deletion.planned))

for message in result.messages:
    print(message)

for error in result.errors:
    print(f"ERROR: {error}")