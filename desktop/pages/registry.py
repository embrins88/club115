print("Loading registry.py...")

from desktop.pages.minecraft_page import MinecraftPage

print("Imported MinecraftPage successfully.")

PAGE_REGISTRY = {
    "minecraft": MinecraftPage,
}

print("PAGE_REGISTRY created.")