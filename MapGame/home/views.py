from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import UserToken
from .forms import CommandForm
from .utils import send_command_to_server, ResponseHandler
from PIL import Image
from io import BytesIO
import base64

from PIL import Image, ImageFilter


def mask_image(image_path,save_path, vision_x, vision_y, blur=False):
    if image_path is not None:
        # Load the image
        image = Image.open(image_path)
        width, height = image.size

        # Create a new image for the mask
        mask = Image.new('L', (width, height), 0)  # 'L' for greyscale
        for x in range(width):
            for y in range(height):
                if x > vision_x or y > vision_y:
                    mask.putpixel((x, y), 255)  # White where we want the effect

        # Apply the effect based on the mask
        if blur:
            # Apply blur effect
            blurred_image = image.filter(ImageFilter.GaussianBlur(5))  # example blur radius
            image.paste(blurred_image, mask=mask)
        else:
            # Apply black effect
            black_image = Image.new('RGB', (width, height), (0, 0, 0))
            image.paste(black_image, (0, 0), mask)

        # Save the modified image
        image.save(save_path)


@login_required
def home(request):
    return render(request, "home.html")

@login_required
def command(request):
    form = CommandForm()
    if request.method == "POST":
        form = CommandForm(request.POST)
        if form.is_valid():
            command = form.cleaned_data["command"]
            # do something with your results
            # Fetch the user's token from the database
            token = UserToken.objects.get(user=request.user)
            response = send_command_to_server(command, auth_token=token.token)
            auth_token = request.session.get('auth_token')
            objects,image_path,vision_x,vision_y = ResponseHandler.handle_response(response,auth_token)
            import os
            
            if image_path is not None:
                image_rel_path = os.path.join(os.path.dirname(os.getcwd()),"MapBackend", image_path)
                print(os.path.exists(image_rel_path), image_rel_path)
                save_path = "static/map.png"
                # Mask the image with the  when x > vision_x and y > vision_Y
                mask_image(image_rel_path, save_path, vision_x, vision_y, blur=True)
                return render(request, "command.html", {"form": form, "command": command, "received":True,"response": response, "objects": objects, "image_path": "../static/map.png"})
            else:
                return render(request, "command.html", {"form": form, "command": command, "received":True,"response": response, "objects": objects})
    return render(request, "command.html", {"form": form, "received":False})
    

