from servers.services.server_config import get_server
from servers.workflows.sync_workflow import SyncWorkflow


server = get_server("homestead")
workflow = SyncWorkflow(server)
result = workflow.run()

print("Server:", result.server_name)
print("Succeeded:", result.succeeded)
print("Completed steps:", result.completed_steps)

if result.comparison:
    print(
        "Changes:",
        result.comparison.total_changes,
    )

if result.checkpoint:
    print(
        "Checkpoint:",
        result.checkpoint.checkpoint_id,
    )

for message in result.messages:
    print(message)

for error in result.errors:
    print(f"ERROR: {error}")