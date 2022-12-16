from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import  auth
from .models import User, Contact, Subscribe, QRCollection
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.urls import reverse_lazy, reverse
import os
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, force_str,DjangoUnicodeDecodeError
from django.core.mail import EmailMessage
from qr_generaator.settings import MEDIA_URL, STATIC_ROOT, STATIC_URL, MEDIA_ROOT
from django.conf import settings
import random
import os
from django.http.response import HttpResponse
from PIL import Image, ImageDraw
import mimetypes
import base64

# Create your views here.

def index(request):
    if request.user.is_authenticated:
        return redirect('generator:dashboard')
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        subscriber = Subscribe.objects.filter(email = email).exists()
        if subscriber:
            messages.info(request, 'You are already a subscriber')
        else:
            subscriber = Subscribe.objects.create(name = name, email=email)
            subscriber.save()
            messages.info(request, 'You have successfully subscribed to our email service')

    context = {}
    return render(request, "generator/index.html", context)

def login(request):
    if request.method == 'POST':
        email= request.POST['email']
        password = request.POST['password']
        if User.objects.filter(email=email).exists():
            user = auth.authenticate(email=email,password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('generator:dashboard')

            else:
                messages.info(request, 'Invalid credentials')
                return redirect('generator:login')
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('generator:login')
    return render(request, "generator/login.html")


# ============================================
# ============================================


def logout(request):
    auth.logout(request)
    return redirect('/')


# =============================================
# =============================================

def aboutus(request):
    return render(request, "generator/aboutus.html")
def faq(request):
    return render(request, "generator/faq.html")
def contactus(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        contact = Contact.objects.create(name = name, email=email, message = message)
        contact.save()
        messages.info(request, "Your message has been sent successfully")
        return redirect('generator:index')


    return render(request, "generator/contactus.html")

def signup(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone_num= request.POST['phone_number']  
        password = request.POST['password']
        pass2 = request.POST['password2']
        email = email.lower()
        if password == pass2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email already exist")
                return redirect('generator:signup')
            else:

                user = User.objects._create_user(email, password, name, phone_num)
                user.save()
        else:
            messages.info(request, "Password didnt match")
            return redirect('generator:signup')
        auth.login(request, user)
        return redirect('generator:dashboard')
        # messages.info(request, "Account created, check your email for activation link")
        # return redirect('generator:login')
        
    return render(request, "generator/signup.html")


class dashboard(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        qr = QRCollection.objects.filter(qr_user = user)
        print(qr)
        context={"user":user, "qr": qr}
        return render(request, "generator/dashboard.html",context)
    # def post(self,request,response):
    #     user = request.user
    #     return render(request, "generator/dashboard.html",context)

class generate_qr(LoginRequiredMixin, View):
    def post(self, request):
        if 'text' in request.POST:
            QRCollection.objects.create(
                qr_user = request.user,
                category = 'TEXT',
                qr_info = 'Your Text is: ' + request.POST['text'],
                )

            ls = QRCollection.objects.all().order_by('-id')[0]
            context = {'qr_image':ls}
            user = request.user
            context={"user":user}
            return redirect('generator:dashboard')
            # return render(request, "generator/dashboard.html",context)

        elif 'url-link' in request.POST:
            QRCollection.objects.create(
                qr_user = request.user,
                category = 'URL',
                qr_info = 'Your Link is: ' + request.POST['url-link'],
                )
            user = request.user
            context={"user":user}
            return redirect('generator:dashboard')


        # if App-store is selected
        elif 'app-store' in request.POST:
            QRCollection.objects.create(
                qr_user = request.user,
                category = 'URL',
                qr_info = 'Your App-store Link is: ' + request.POST['app'],
                )

            ls = QRCollection.objects.all().order_by('-id')[0]
            context = {'qr_image':ls}

            return redirect('generator:dashboard')
    def get(self, request):
        return render(request, 'generator/generateqr.html')

def convert_to_jpeg(path):
    image = Image.open(path)
    rgb_image = image.convert('RGB')
    jpeg_image = rgb_image.save(path.replace('.png', '.jpeg'), 'JPEG')
    return path.replace('.png', '.jpeg'), os.path.basename(path.replace('.png', '.jpeg'))

def convert_to_png(path):
    image = Image.open(path)
    rgb_image = image.convert('RGB')
    png_image = rgb_image.save(path.replace('.png', '.png'), 'PNG')
    return path.replace('.png', '.png'), os.path.basename(path.replace('.png', '.png'))

# Convert to JPG
def convert_to_jpg(path):
    image = Image.open(path)
    rgb_image = image.convert('RGB')
    jpg_image = rgb_image.save(path.replace('.png', '.jpg'), 'JPG')
    return path.replace('.png', '.jpg'), os.path.basename(path.replace('.png', '.jpg'))


# Convert to SVG
def convert_to_svg(path):
    startSvgTag = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
    "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg version="1.1"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    width="240px" height="240px" viewBox="0 0 240 240">"""
    endSvgTag = """</svg>"""
    pngFile = open(path, 'rb')
    base64data = base64.b64encode(pngFile.read())
    base64String = '<image xlink:href="data:image/png;base64,{0}" width="240" height="240" x="0" y="0" />'.format(base64data.decode('utf-8'))
    f = open(path.replace('.png', '.svg'), 'w')
    f.write(startSvgTag + base64String + endSvgTag)
    f.close()
    return path.replace('.png', '.svg'), os.path.basename(path.replace('.png', '.svg'))


# Convert to PDF
def convert_to_pdf(path):
    image = Image.open(path)
    rgb_image = image.convert('RGB')
    pdf_image = rgb_image.save(path.replace('.png', '.pdf'), 'PDF')
    return path.replace('.png', '.pdf'), os.path.basename(path.replace('.png', '.pdf'))


class download_file(LoginRequiredMixin, View):
    def get(self, request, id, file_type):
        if (id == "" or file_type == ""):
            messages.info(request, "invalid download credentials")
            return redirect('generator:dashboard')
        qr = QRCollection.objects.get(id=id, qr_user = request.user).qr_code
        obj = MEDIA_ROOT + '/' + str(qr)

        if file_type == "pdf":
            filepath, filename = convert_to_pdf(obj)
        elif file_type == "png":
            filepath, filename = convert_to_png(obj)
        elif file_type == "jpg":
            filepath, filename = convert_to_jpg(obj)
        elif file_type == "svg":
            filepath, filename = convert_to_svg(obj)
        elif file_type == "jpeg":
            filepath, filename = convert_to_jpeg(obj)
        path = open(filepath, 'rb')
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response
            


class delete_file(LoginRequiredMixin, View):
    def get(self, request, id):
        try:
            QRCollection.objects.get(id=id, qr_user = request.user).delete()
            return redirect('generator:dashboard')
        except:
            return redirect('generator:dashboard')


class genqr2(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'generator/qrContent.html')
    def post(self, request):
        qr_name = request.POST["name"]
        qr_url = request.POST["text"]
        request.session["qr_name"] = qr_name
        request.session["qr_name"] = qr_url
        return redirect('generator:download_qr')
class qr_design(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'generator/qr_design.html')

class download_qr(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'generator/download.html')
    def post(self, request):
        file_type = request.POST["type"]
        file_type = file_type.lower()
        qr_name = request.session.get("qr_name")
        qr_url = request.session.get("qr_url")
        try:
            qr = QRCollection.objects.create(
                    qr_user = request.user,
                    category = 'TEXT',
                    qr_info = qr_name,
                    )
            qr = qr.qr_code
        except:
            qr = "default.jpeg"
        obj = MEDIA_ROOT + '/' + str(qr)
        if file_type == "pdf":
            filepath, filename = convert_to_pdf(obj)
        elif file_type == "png":
            filepath, filename = convert_to_png(obj)
        elif file_type == "jpg":
            filepath, filename = convert_to_jpg(obj)
        elif file_type == "svg":
            filepath, filename = convert_to_svg(obj)
        elif file_type == "jpeg":
            filepath, filename = convert_to_jpeg(obj)
        path = open(filepath, 'rb')
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response

        return render(request, 'generator/qr_design.html')