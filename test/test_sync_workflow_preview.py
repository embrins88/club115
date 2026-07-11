from servers.services.server_config import get_server
from servers.workflows.sync_workflow import SyncWorkflow


server = get_server("homestead")

result = SyncWorkflow(
    server,
    dry_run=True,
).run()

print("Server:", result.server_name)
print("Succeeded:", result.succeeded)
print("Steps:", result.completed_steps)

if result.upload:
    print()

    print("Would upload:")

    for path in result.upload.planned:
        print(f"  {path}")

if result.deletion:
    print()

    print("Would delete:")

    for path in result.deletion.planned:
        print(f"  {path}")