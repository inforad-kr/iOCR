from django.contrib import admin

from .models import ImgRecord, UserImg, SmallImg

admin.site.register(UserImg)
# admin.site.register(ImgRecord)

class ImgRecordAdmin(admin.ModelAdmin):
    list_display = ('user_img', "content", 'quality', 'user_content', 'checked', 'image_file')
admin.site.register(ImgRecord, ImgRecordAdmin)

class SmallImgAdmin(admin.ModelAdmin):
    list_display = ('parent_pic', "content", 'quality', 'user_content', 'checked', 'image_file', 'unrecognizable')
admin.site.register(SmallImg, SmallImgAdmin)

