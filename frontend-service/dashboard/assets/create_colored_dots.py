from PIL import Image, ImageDraw

# define the image size and background color
image_size = (50, 50)
background_color = (0, 0, 0, 0)

# create a new image with the specified size and background color
image = Image.new("RGBA", (50, 50), (0, 0, 0, 0))

# create a drawing object to draw on the image
draw = ImageDraw.Draw(image)

# define the circle's position and size
circle_center = (25, 25)
circle_radius = 10

# define the circle color (red in RGB) and draw
circle_color = (0, 255, 0, 255)
draw.ellipse([circle_center[0] - circle_radius, circle_center[1] - circle_radius,
              circle_center[0] + circle_radius, circle_center[1] + circle_radius],
             fill=circle_color, outline=circle_color)

# save the image as a ICO file
ico_sizes = [(16, 16), (32, 32), (48, 48)]
image.save("./yellow_circle_dot.ico",  sizes=ico_sizes)
print("yellow circle dot indicator ICO file created and saved.")
image.close()
#image.save(f"./{color_description}_circle_dot.ico", format="ico")

# # define the circle color (green in RGB) and draw
# circle_color = (0, 255, 0, 255)
# draw.ellipse([circle_center[0] - circle_radius, circle_center[1] - circle_radius,
#               circle_center[0] + circle_radius, circle_center[1] + circle_radius],
#              fill=circle_color, outline=circle_color)

# # save the image as a PNG file
# image.save("./green_circle_dot.png", format="PNG")
# image.close()
# print("Green circle dot indicator PNG file created and saved.")

# # message_background_color = "#ff0303" #= "red"
# # message_background_color = "#03ff1c" #= "green"
