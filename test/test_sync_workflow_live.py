from servers.services.server_config import get_server
from servers.workflows.sync_workflow import SyncWorkflow


server = get_server("homestead")

answer = input(
    "Run LIVE sync on Homestead? This will modify the server. (y/N): "
).strip().lower()

if answer != "y":
    print("Cancelled.")
    raise SystemExit

result = SyncWorkflow(
    server,
    dry_run=False,
).run()

print("\nServer:", result.server_name)
print("Succeeded:", result.succeeded)
print("Steps:", result.completed_steps)

if result.checkpoint:
    print("Checkpoint:", result.checkpoint.checkpoint_id)

if result.upload:
    print("Uploaded:", result.upload.files_uploaded)

if result.deletion:
    print("Deleted:", result.deletion.files_deleted)

for message in result.messages:
    print(message)

for error in result.errors:
    print(f"ERROR: {error}")