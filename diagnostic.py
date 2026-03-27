import pygame
import sys
from OpenGL.GL import *

def diagnostic():
    print("--- Kenji 3D Object Renderer Diagnostic ---")
    print(f"Python Version: {sys.version}")
    
    try:
        pygame.init()
        print("✅ Pygame initialized successfully.")
    except Exception as e:
        print(f"❌ Pygame failed to initialize: {e}")
        return

    try:
        # Check for display drivers
        drivers = pygame.display.get_driver()
        print(f"✅ Video Driver: {drivers}")
        
        # Try to get display info
        info = pygame.display.Info()
        print(f"✅ Current Resolution: {info.current_w}x{info.current_h}")
    except Exception as e:
        print(f"❌ Failed to get display info: {e}")

    try:
        # Attempt to create a small OpenGL window
        pygame.display.set_mode((100, 100), pygame.DOUBLEBUF | pygame.OPENGL)
        version = glGetString(GL_VERSION).decode()
        vendor = glGetString(GL_VENDOR).decode()
        renderer = glGetString(GL_RENDERER).decode()
        print(f"✅ OpenGL Version: {version}")
        print(f"✅ OpenGL Vendor: {vendor}")
        print(f"✅ OpenGL Renderer: {renderer}")
    except Exception as e:
        print(f"❌ OpenGL window creation failed: {e}")
        print("   This usually means missing drivers or an incompatible environment (e.g., SSH/Docker).")

    pygame.quit()

if __name__ == "__main__":
    diagnostic()
