from servers.services.checkpoint_service import CheckpointService
from servers.services.comparison_service import ComparisonService
from servers.services.server_config import get_server


server = get_server("homestead")

comparison = ComparisonService(server).run()

if comparison.errors:
    for error in comparison.errors:
        print(f"ERROR: {error}")
    raise SystemExit(1)

checkpoint = CheckpointService(
    server,
    comparison,
).run()

print("Checkpoint created")
print("ID:", checkpoint.checkpoint_id)
print("Directory:", checkpoint.remote_directory)
print("Files saved:", checkpoint.files_saved)
print("Archive:", checkpoint.archive_path)