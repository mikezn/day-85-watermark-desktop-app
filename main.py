import tkinter.filedialog
from tkinter import *
from PIL import Image, ImageTk, ImageDraw, ImageOps

BACKGROUND_COLOUR ='#2e2e2e'
img_background_pil = None
img_background_tk = None
img_watermark_pil = None
process_watermark_pil = None
CANVAS_SIZE = (800, 526)
ROUNDING_RADIUS = 15


# This function handles the uploading of both the background and watermark image.
'''image bool represents if it's the background to be watermarked (True), or the watermark itself (False). This is a common 
function to read in all images'''
def upload_image(dimensions, background):
    file_path = tkinter.filedialog.askopenfilename(
        title='Upload Image',
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )

    if not file_path:
        print("No file selected.")
        return None

    # Open and process the PIL image
    img_raw = Image.open(file_path).convert('RGBA')
    img_raw.thumbnail(dimensions, Image.Resampling.LANCZOS)

    if background:
        # Return both PIL and Tkinter images for the background
        # PIL is for the processing, Tkinter is to display the uploaded image for the user to see
        img_tk = ImageTk.PhotoImage(add_rounded_corners(img_raw, ROUNDING_RADIUS))
        return img_raw, img_tk
    else:
        # Just return the PIL image for the watermark
        return img_raw


#adds rounded corners to background image
def add_rounded_corners(img, radius):
    # Ensure image has an alpha channel
    img = img.convert("RGBA")

    # Create a mask the same size as the image, filled with transparent pixels
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)

    # Draw a white rounded rectangle on the mask
    draw.rounded_rectangle((0, 0, *img.size), radius=radius, fill=255)

    # Apply the rounded corner mask to the image
    rounded_img = ImageOps.fit(img, img.size, centering=(0.5, 0.5))
    rounded_img.putalpha(mask)

    return rounded_img


# This application runs all off one button, so this function handles all the clicks from the button
# depending on the state of the button which is determined by the button text
def btn_upload_save():
    global img_background_pil, img_background_tk, img_watermark_pil, process_watermark_pil

    if btn_upload_img.cget("text") == "Upload Image":
        result = upload_image((CANVAS_SIZE[0]-10, CANVAS_SIZE[1]-10), background=True)
        if result is not None:
            img_background_pil, img_background_tk = result  # Unpack the tuple
            canvas.itemconfig(img_can, image=img_background_tk)
            canvas.image = img_background_tk
            btn_upload_img.config(text='Upload Watermark',
                                  image=img_btn_upload_watermark)

            #change polygon size to resize around the background image
            x1, y1 = 0, 0
            x2, y2 = CANVAS_SIZE[0] -5, img_background_tk.height()+10
            rectangle_points = [
                x1, y1,
                x2, y1,
                x2, y2,
                x1, y2
            ]
            canvas.coords(polygon_id, get_rounded_rect_points(x1, y1, x2, y2, 30))


        else:
            print("No background image selected.")

    elif btn_upload_img.cget("text") == "Upload Watermark":
        result = upload_image((200, 100), background=False)
        if result is not None:
            img_watermark_pil = result

            # Before calling add_watermark(), check that img_background_pil isn't None
            if img_background_pil is None:
                print("Background image is missing!")
                return

            process_watermark_pil = add_watermark(img_background_pil, img_watermark_pil)
            img_watermarked_tk = ImageTk.PhotoImage(process_watermark_pil)

            canvas.itemconfig(img_can, image=img_watermarked_tk)
            canvas.image = img_watermarked_tk

            btn_upload_img.config(text='Save Image', image=img_btn_save_img)

        else:
            print("No watermark image selected.")

    elif btn_upload_img.cget("text") == "Save Image":
        if save_final_image(process_watermark_pil):
            btn_upload_img.config(text='Upload Image')


# main watermarking function takes in both the background and watermark as PIL images for processing
def add_watermark(base, watermark):
    # Position the watermark at bottom-right
    position = (
        base.width - watermark.width - 10,
        base.height - watermark.height - 10
    )

    # Create new image for combining
    transparent = Image.new("RGBA", base.size)
    transparent.paste(base, (0, 0))
    transparent.paste(watermark, position, mask=watermark)

    # Convert to RGB to remove alpha (useful for saving/displaying as JPEG)
    return transparent.convert("RGB")


def save_final_image(img):
    if img is None:
        print("No image to save!")
        return

    file_path = tkinter.filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
    )

    if file_path:
        img.save(file_path)
        print(f"Image saved to {file_path}")
        return True
    else:
        print("Save cancelled.")

def get_rounded_rect_points(x1, y1, x2, y2, radius):
    return [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]


window = Tk()
window.title = "Watermarker"
window.config(padx=50, pady=50, bg=BACKGROUND_COLOUR)

canvas = Canvas(width=CANVAS_SIZE[0], height=CANVAS_SIZE[1], bg=BACKGROUND_COLOUR, highlightthickness=0)
img_can = canvas.create_image(5, 5, anchor='nw')

polygon_id = canvas.create_polygon(get_rounded_rect_points(0, 0, CANVAS_SIZE[0], CANVAS_SIZE[1], 50),
                                   outline="#00ffcc",  # Border color
                                   width=5,  # Border thickness
                                   dash=(10, 10),  # Dotted/Dashed pattern
                                   fill="",# No fill
                                   smooth=True
                                   )

img_btn_upload_background = PhotoImage(file="./images/btn_upload_background.png")
img_btn_upload_watermark = PhotoImage(file="./images/btn_upload_watermark.png")
img_btn_save_img = PhotoImage(file="./images/btn_save_img.png")

btn_upload_img = Button(image=img_btn_upload_background,
                        command=btn_upload_save,
                        borderwidth=5,
                        highlightthickness=0,
                        relief='flat',
                        background=BACKGROUND_COLOUR,
                        padx=0,
                        pady=0,
                        text='Upload Image')

canvas.grid(column=0, row=0, columnspan=1)
btn_upload_img.grid(column=0, row=1)

window.mainloop()