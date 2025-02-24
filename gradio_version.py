import gradio as gr
from ice_analyzer import analyze_warrant
import mimetypes

with gr.Blocks() as demo: # Create the application named "demo"
    gr.Markdown("""
# ICE Warrant Analyzer
This is an experimental tool to analyze ICE warrants using an AI tool from Google. The data you submit may be used by Google for training purposes.
""")
    with gr.Row():
        with gr.Column():
            input_choice = gr.Radio(label="Choose input method:", choices=["Upload File", "Capture Image"], value="Upload File", interactive=True)
            upload = gr.File(label="Upload a file", type="filepath", file_types=[".jpg",".jpeg",".png",".pdf"])
            picture = gr.Image(label="Capture an image of the warrant using your camera.", sources=["webcam"],visible=False,type="filepath")
        with gr.Column(): # Not technically necessary, but easier to read.
            gr.Markdown("## Analysis")
            output = gr.Markdown("")

    def show_inputs(input_choice):
        # The output is upload, then image, so we change visibility on both accordingly
        if input_choice == "Upload File":
            return gr.update(visible=True), gr.update(visible=False)
        else:
            return gr.update(visible=False), gr.update(visible=True)

    def process_upload(upload):
        # This is just designed to generate theinputs that the analyze_warrant function expects
        # Not even sure if it works.
        if upload is None:
            return ""
        mime_type, _ = mimetypes.guess_type(upload)
        with open(upload, "rb") as f:
            file_bytes = f.read()
        gr.Info("Analyzing the warrant, please wait...")
        result = analyze_warrant(file_bytes, mime_type)
        gr.Info("Analysis Complete")
        return result

    # Defining behaviour:
    # {component}.{event}({name of function to call}, {list of input components}, {list of output components})

    # If the input choice changes, change the visibiity of the inputs
    input_choice.change(show_inputs,[input_choice],[upload,picture])

    # If the user takes a picture, make the picture the upload
    picture.change(lambda x: x,[picture],[upload])

    # If the upload changes, process it and generate a new output if necessary
    upload.change(process_upload,[upload],[output])

    
demo.launch() # Launch the application