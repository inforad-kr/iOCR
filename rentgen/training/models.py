from django.db import models
from django.utils import timezone

class UserImg(models.Model): 
    image_file = models.ImageField(upload_to='images/', blank=True)


    def __str__(self): 
        return f"{self.id},  {self.image_file}"
    
    class Meta:
        # verbose_name_plural = "Files for recognition" 
        # verbose_name =  "File for recognition" 
        verbose_name_plural = "Uploaded images" 
        verbose_name =  "Uploaded image" 

class ImgRecord(models.Model):
#    title = models.CharField(max_length=200)
    # file_name = models.CharField(max_length=30, verbose_name='File name', unique=True)
    user_img = models.ForeignKey(UserImg, on_delete=models.CASCADE, verbose_name='Parent picture')
    # parent =
    image_file = models.ImageField(upload_to='images/', blank=True)
    quality = models.DecimalField(max_digits=7, decimal_places=5)
    content = models.CharField(max_length=30, blank=True, verbose_name='AI recognition')
    user_content = models.CharField(max_length=30, blank=True, verbose_name='Human recognition')
    date_created = models.DateTimeField(default=timezone.now)
    unrecognizable = models.BooleanField(default=False, verbose_name='Unrecognizable')
    checked = models.BooleanField(default=False, verbose_name='Verified by a human')
    
    def __str__(self): 
        return f"{self.image_file}" 
    
    class Meta:
        # verbose_name_plural = "Files for recognition" 
        # verbose_name =  "File for recognition" 
        verbose_name_plural = "Files for training" 
        verbose_name =  "File for training" 


class SmallImg(models.Model):
#    title = models.CharField(max_length=200)
    # file_name = models.CharField(max_length=30, verbose_name='File name', unique=True)
    # user_img = models.ForeignKey(UserImg, on_delete=models.CASCADE, verbose_name='Parent picture')
    parent_pic = models.CharField(max_length=50, blank=True, verbose_name='Parent pic name')
    # parent =
    image_file = models.ImageField(upload_to='images/', blank=True)
    quality = models.DecimalField(max_digits=7, decimal_places=5)
    content = models.CharField(max_length=30, blank=True, verbose_name='AI recognition')
    user_content = models.CharField(max_length=30, blank=True, verbose_name='Human recognition')
    date_created = models.DateTimeField(default=timezone.now)
    unrecognizable = models.BooleanField(default=False, verbose_name='Unrecognizable')
    checked = models.BooleanField(default=False, verbose_name='Verified by a human')
    
    def __str__(self): 
        return f"{self.image_file}" 
    
    class Meta:
        # verbose_name_plural = "Files for recognition" 
        # verbose_name =  "File for recognition" 
        verbose_name_plural = "Pics for training" 
        verbose_name =  "Pic for training" 