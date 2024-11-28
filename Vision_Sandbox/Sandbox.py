from PIL import Image

# Creating placeholder images
user_images = [Image.new('RGB', (200, 200), color) for color in ["#add8e6", "#90ee90", "#ffcccb", "#f4a460"]]
canvas = Image.new('RGB', (800, 600), 'white')

# Positioning user-generated content
x, y = 50, 50
for img in user_images:
    canvas.paste(img, (x, y))
    x += 210

canvas.save("advocacy_ugc_showcase.png")
