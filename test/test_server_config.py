from servers.services.server_config import get_server, load_config


config = load_config()
homestead = get_server("homestead")

print("SSH host:", config["ssh"]["host"])
print("Server ID:", homestead.server_id)
print("Server name:", homestead.name)
print("Local instance:", homestead.local_instance)
print("Local mods:", homestead.local_mods)
print("Remote root:", homestead.remote_root)
print("Remote mods:", homestead.remote_mods)
print("Service:", homestead.service)
print("Game port:", homestead.game_port)
print("RCON port:", homestead.rcon_port)
print("World:", homestead.world_name)