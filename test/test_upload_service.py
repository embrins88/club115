from servers.services.comparison_service import ComparisonService
from servers.services.server_config import get_server
from servers.services.upload_service import UploadService


server = get_server("homestead")
comparison = ComparisonService(server).run()

if comparison.errors:
    for error in comparison.errors:
        print(f"ERROR: {error}")
    raise SystemExit(1)

print("Files that would be uploaded:")
for change in comparison.added + comparison.updated:
    print(f"  - {change.path}")

print()
answer = input(
    "Upload these files to Homestead? (y/N): "
).strip().lower()

if answer != "y":
    print("Cancelled.")
    raise SystemExit

result = UploadService(
    server,
    comparison,
).run()

print()
print("Upload complete.")
print(f"Uploaded: {result.files_uploaded}")

if result.errors:
    print("\nErrors:")
    for error in result.errors:
        print(f" - {error}")