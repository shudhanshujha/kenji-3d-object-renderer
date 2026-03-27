import gradio as gr
import os

def render_3d(mesh_file):
    """Passes the mesh file directly to the Model3D viewer."""
    if mesh_file is None:
        return None
    return mesh_file.name

# --- Interface Setup ---
with gr.Blocks(title="Kenji 3D Object Renderer Preview") as demo:
    gr.Markdown("# 🚀 Kenji 3D Object Renderer (Web Preview)")
    gr.Markdown("Interact with 3D models directly in your browser. Supports `.obj`, `.stl`, `.glb`, and `.gltf`.")
    
    with gr.Row():
        with gr.Column(scale=1):
            input_file = gr.File(label="Upload 3D Model", file_types=[".obj", ".stl", ".glb", ".gltf"])
            gr.Markdown("### Instructions:")
            gr.Markdown("- **Left Click:** Rotate model")
            gr.Markdown("- **Right Click:** Pan view")
            gr.Markdown("- **Scroll:** Zoom in/out")
            gr.Markdown("- **Double Click:** Reset view")
            
        with gr.Column(scale=2):
            output_3d = gr.Model3D(label="3D Viewport", clear_color=[0.1, 0.1, 0.1, 1.0])
    
    # Connect logic
    input_file.change(fn=render_3d, inputs=input_file, outputs=output_3d)

# Start the local server
if __name__ == "__main__":
    print("Launching Web Preview at http://localhost:7860")
    demo.launch()
