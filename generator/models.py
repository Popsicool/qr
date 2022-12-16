from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import qrcode
import random
from django.core.files import File
from PIL import Image, ImageDraw
from io import BytesIO
from qr_generaator.settings import MEDIA_URL, STATIC_ROOT, STATIC_URL, MEDIA_ROOT


class CustomUserManager(BaseUserManager):
    def _create_user(self,email,password, name, phone_num,  **extra_fields):
        if not email:
            raise valueerror("Email must be provided")
        if not password:
            raise valueerror("Password must be provided")

        user = self.model(
            email  = self.normalize_email(email),
            name = name,
            phone_num = phone_num,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, name, phone_num, **extra_fields):
        extra_fields.setdefault('is_staff',False)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',False)
        return self._create_user(email, password, name, phone_num)

    def create_superuser(self, email, password,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',True)
        return self._create_user(email, password,name=None, phone_num=None, **extra_fields)


class User(AbstractBaseUser,PermissionsMixin):
    email= models.EmailField(unique=True, max_length=254)
    name = models.CharField(max_length=240, null=True)
    phone_num = models.CharField(max_length=50, null=True)
    is_staff = models.BooleanField(default=False)
    is_active =  models.BooleanField(default=True)
    is_superuser =  models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELD = ['email']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Contact(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    message = models.TextField()

    def __str__(self):
        if len(self.message) < 15:
            return self.message
        return self.text[:11] + ' ...'

class Subscribe(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    def __str__(self):
        return self.email

class QRCollection(models.Model):
    """All QR collections available"""
    qr_user = models.ForeignKey(User, on_delete=models.CASCADE, )
    category = models.CharField(max_length=200, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True) 
    qr_code = models.ImageField(upload_to='all_qr/')
    qr_info = models.CharField(max_length=200, blank=True, null=True)

    def save(self,*args,**kwargs):    
        # adjust image size
        QRcode = qrcode.QRCode(
        version=3,
        box_size = 10,
        border=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M
        )
        QRcode.add_data(self.qr_info)
        QRcode.make(fit=True)
    
        QRimg = QRcode.make_image(
            fill_color='black', back_color="white").convert('RGB')

         # set size of QR code
        buffer=BytesIO()
        QRimg.save(buffer, 'PNG')
        self.qr_code.save(f'{self.qr_user.name}{random.randint(0,9999)}.png',File(buffer),save=False)
        print(self.qr_code)
        super().save(*args,**kwargs)

    def __str__(self):
        return f'{self.qr_user.name}\'s {self.category}'


    class Meta:
        db_table = 'qr_collection'
        verbose_name_plural = 'qr_collections'