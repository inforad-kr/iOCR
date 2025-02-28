# sudo rmmod nvidia_uvm
# sudo modprobe nvidia_uvm
from django.shortcuts import render
from .models import ImgRecord
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from .models import UserImg, SmallImg
from django.contrib.auth import logout
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.shortcuts import render
from .forms import EditAndCheckForm, ImageUploadForm 
from django.http import JsonResponse
from io import BytesIO
import easyocr
import numpy as np
from PIL import Image
import time
import json
from json import JSONEncoder
from django.db.models import Max
import os
from django.conf import settings
from django.core.files.base import ContentFile
from .globals import reader
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import Levenshtein
import csv
import shutil
from django.http import HttpResponse


@csrf_exempt
def recordnition_image_api(request):
    time1 = time.time()
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_image = request.FILES['image']
        file_format = os.path.splitext(uploaded_image.name)[-1].lower()
        if file_format.startswith('.'):
            file_format = file_format[1:]
        if not file_format == 'jpg':
            return render(request,'training/error_page.html') 
        image = Image.open(uploaded_image)
        user_img = UserImg(image_file=request.FILES['image'])
        parent_directory, original_filename = os.path.split(uploaded_image.name)
        base_name, file_extension = os.path.splitext(original_filename)
        image_array = np.array(image)
        # result = reader.readtext(image_array, detail=1)
        result = reader.readtext(image_array, detail=1, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-', width_ths=0,
                                 height_ths=0, link_threshold=1, low_text=0.5, contrast_ths=0.05, decoder='beamsearch')
        count = 0
        recognized_imgs = []
        single_char = request.GET.get('single', 'false').lower() == 'true'
        
        result_dict = {
                'regions_of_interest': [
                    {
                        'coordinates': roi[0],
                        'text': roi[1][:1] if single_char else roi[1],
                        'confidence': roi[2]
                    }
                    for roi in result
                ]
            }
        json_result = json.dumps(result_dict, indent=4, cls=NumpyEncoder)
        print(time.time() - time1)
        # return JsonResponse({'message': 'Image uploaded successfully.'})
        #return JsonResponse(json_result, safe=False)
        #return JsonResponse(json_result, safe=False, json_dumps_params={'ensure_ascii': False})
        return HttpResponse(json_result, content_type="application/json")


    else:
        return JsonResponse({'message': 'Image upload failed.'}, status=400)

@csrf_exempt
def upload_image_api(request):
    time1 = time.time()
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_image = request.FILES['image']
        file_format = os.path.splitext(uploaded_image.name)[-1].lower()
        if file_format.startswith('.'):
            file_format = file_format[1:]
        if not file_format == 'jpg':
            return render(request,'training/error_page.html') 
        image = Image.open(uploaded_image)
        user_img = UserImg(image_file=request.FILES['image'])
        parent_directory, original_filename = os.path.split(uploaded_image.name)
        base_name, file_extension = os.path.splitext(original_filename)
        image_array = np.array(image)
        result = reader.readtext(image_array, detail=1)
        count = 0
        recognized_imgs = [] 
        for res in result:
            coordinates = res[0]
            x_values, y_values = zip(*coordinates)
            left = min(x_values)
            upper = min(y_values)
            right = max(x_values)
            lower = max(y_values)
            roi = image.crop((left, upper, right, lower))
            roi = roi.convert("RGB")
            new_filename = f"{base_name}_{count}{file_extension}"
            print(res[1], new_filename)
            count = count + 1 
            buffer = BytesIO()
            roi.save(buffer, format="JPEG")
            roi = image.crop((left, upper, right, lower))
            roi = roi.convert("RGB")
            new_record = SmallImg()
            new_record.parent_pic = original_filename
            new_record.image_file.save(new_filename, ContentFile(buffer.getvalue()), save=False)
            new_record.quality = res[2]
            new_record.content = res[1]
            new_record.save()
            recognized_imgs.append(new_record)
        result_dict = {
                'regions_of_interest': [
                    {
                        'coordinates': roi[0],
                        'text': roi[1],
                        'confidence': roi[2]
                    }
                    for roi in result
                ]
            }
        json_result = json.dumps(result_dict, indent=4, cls=NumpyEncoder)
        print(time.time() - time1)
        return JsonResponse({'message': 'Image uploaded successfully.'})
        # return JsonResponse(json_result, safe=False)
    else:
        return JsonResponse({'message': 'Image upload failed.'}, status=400)



class NumpyEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64):
            return int(obj)
        if isinstance(obj, np.int32):
            return int(obj)
        return super(NumpyEncoder, self).default(obj)
    

def fst_rec(request):
    time1 = time.time()
    single_rec = False
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.cleaned_data['image_file']
            file_format = os.path.splitext(uploaded_image.name)[-1].lower()
            if file_format.startswith('.'):
                file_format = file_format[1:]
            if not file_format == 'jpg':
                return render(request,'training/error_page.html') 

            image = Image.open(uploaded_image)
            user_img = UserImg(image_file=request.FILES['image_file'])
            # user_img.save()

            parent_directory, original_filename = os.path.split(uploaded_image.name)
            base_name, file_extension = os.path.splitext(original_filename)
            image_array = np.array(image)
            
            # result = reader.readtext(image_array, detail=1)
            single_rec = request.POST.get("single_rec")
            if single_rec:
                result = reader.readtext(image_array, detail=1, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-',
                                         width_ths=0, height_ths=0, link_threshold=1, low_text=0.5, contrast_ths=0.05,
                                         decoder='beamsearch')
            else:
                result = reader.readtext(image_array, detail=1, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-',
                                         decoder='beamsearch')
            count = 0
            recognized_imgs = [] 
            for res in result:
                coordinates = res[0]
                x_values, y_values = zip(*coordinates)
                left = min(x_values)
                upper = min(y_values)
                right = max(x_values)
                lower = max(y_values)
                print(res[1])
                roi = image.crop((left, upper, right, lower))
                roi = roi.convert("RGB")
                new_filename = f"{base_name}_{count}{file_extension}"
                print(new_filename)
                count = count + 1 
                buffer = BytesIO()
                roi.save(buffer, format="JPEG")
                roi = image.crop((left, upper, right, lower))
                roi = roi.convert("RGB")
                new_record = SmallImg()
                new_record.parent_pic = original_filename
                new_record.image_file.save(new_filename, ContentFile(buffer.getvalue()), save=False)
                new_record.quality = res[2]
                new_record.content = res[1]
                new_record.save()
                recognized_imgs.append(new_record)
            
            data = {
                'form' : form,
                # 'json_result' : json_result
                'recognized_imgs' : recognized_imgs,
                'original_filename' : original_filename
            }
        else:
            data = {'form' : form,}

    else:
        form = ImageUploadForm()
        data = {'form' : form,}
    time2 = time.time()
    print('recognition time ', time2 - time1)
    return render(request, 'training/smallimg_form.html', {'data': data, 'single_rec': single_rec})

def recognition(request):
    # print('request.method',request.method)
    time1 = time.time()
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            uploaded_image = form.cleaned_data['image_file']
            file_format = os.path.splitext(uploaded_image.name)[-1].lower()
            if file_format.startswith('.'):
                file_format = file_format[1:]
            if not file_format == 'jpg':
                return render(request,'training/error_page.html') 

            image = Image.open(uploaded_image)
            # max_id = UserImg.objects.aggregate(Max('id'))['id__max']
            # if max_id is not None:
            #     max_id = max_id + 1
            # else:
            #     max_id = 0
            # image.convert("RGB")
            # media_path = os.path.join(settings.MEDIA_ROOT, 'upload_img')
            # image_path = os.path.join(media_path, f"{max_id}.jpg")
            # image.save(image_path, "JPEG")
            # new_record = UserImg()
            # new_record.image_file = 

            user_img = UserImg(image_file=request.FILES['image_file'])
            user_img.save()

            parent_directory, original_filename = os.path.split(uploaded_image.name)
            base_name, file_extension = os.path.splitext(original_filename)
            image_array = np.array(image)
            
            result = reader.readtext(image_array, detail=1)
            count = 0
            recognized_imgs = [] 
            for res in result:
                coordinates = res[0]
                x_values, y_values = zip(*coordinates)
                left = min(x_values)
                upper = min(y_values)
                right = max(x_values)
                lower = max(y_values)
                print(res[1])
                roi = image.crop((left, upper, right, lower))
                roi = roi.convert("RGB")
                new_filename = f"{base_name}_{count}{file_extension}"
                print(new_filename)
                count = count + 1 
                buffer = BytesIO()
                roi.save(buffer, format="JPEG")

                roi = image.crop((left, upper, right, lower))
                roi = roi.convert("RGB")
                new_record = ImgRecord()
                new_record.user_img = user_img
                new_record.image_file.save(new_filename, ContentFile(buffer.getvalue()), save=False)
                new_record.quality = res[2]
                new_record.content = res[1]
                new_record.save()
                recognized_imgs.append(new_record)
                

                # print('new_record.id', new_record.id)
                # new_record.field1 = 'Value 1'
                # new_record.field2 = 42
                # new_record.save()
                # count = count + 1
            # result_dict = {
            #     'regions_of_interest': [
            #         {
            #             'coordinates': roi[0],
            #             'text': roi[1],
            #             'confidence': roi[2]
            #         }
            #         for roi in result
            #     ]
            # }
            # json_result = json.dumps(result_dict, indent=4, cls=NumpyEncoder)
            data = {
                'form' : form,
                # 'json_result' : json_result
                'recognized_imgs' : recognized_imgs
            }
        else:
            data = {
                'form' : form,
            }

    else:
        form = ImageUploadForm()
        data = {
                'form' : form,
            }
    time2 = time.time()
    print('recognition time ', time2 - time1)
    # for result in data['result_dict']:
    # print(data)
    return render(request, 'training/userimg_form.html', {'data': data})


def img_recognition(request):
    if request.method == 'POST':
        print(request)

        response_data = {
            'message': 'Data successfully processed',
            'status': 'success',
            # Add more data as needed
        }

        return JsonResponse(response_data)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)

def additional_training():
    filter_condition = Q(unrecognizable=False) & Q(checked=True) 
    records = SmallImg.objects.filter(filter_condition)
    total = 0
    misstakes = 0
    for rec in records:
        total = total + len(rec.user_content)
        if not rec.content == rec.user_content:
            distance = Levenshtein.distance(rec.user_content, rec.content)
            misstakes = misstakes + distance
            # print(rec.content, rec.user_content)
    if total > 0:
        print('total:',total, ', misstakes:', misstakes, 'misstakes in %:', misstakes*100/total )

def unique_characters():
    filter_condition = Q(unrecognizable=False) & Q(checked=True) 
    records = SmallImg.objects.filter(filter_condition)
    unique_characters = set()
    for rec in records:
        for char in rec.user_content:
            unique_characters.add(char)
    unique_characters_list = list(unique_characters)
    print("List of unique characters:", unique_characters_list)
    # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
        
def make_csv():
    csv_file = "file_contents.csv"
    count = 0
    source_folder = os.path.join(settings.MEDIA_ROOT)  # Replace 'images' with your upload_to folder
    destination_train = os.path.join(settings.MEDIA_ROOT, 'train')
    destination_val = os.path.join(settings.MEDIA_ROOT, 'val')
    # print(destination_train, destination_val)
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["filename", "words"])
        filter_condition = Q(unrecognizable=False) & Q(checked=True) 
        records = SmallImg.objects.filter(filter_condition)
        for rec in records:
            contains_q = 'Q' in rec.user_content
            contains_g = 'G' in rec.user_content
            contains_0 = '0' in rec.user_content

            if not '→' in rec.user_content and len(rec.user_content) > 2:
                if contains_q or contains_g or contains_0:
                    count += 1
                    source_file = os.path.join(source_folder, str(rec.image_file))
                    if count < 155:
                        destination_file = os.path.join(destination_train, str(rec.image_file))
                    else:
                        destination_file = os.path.join(destination_val, str(rec.image_file))
                    # print(source_file, destination_file,rec.user_content)
                    shutil.copy2(source_file, destination_file)    
                    writer.writerow((destination_file,str(rec.user_content)))        
    print(f"CSV file '{csv_file}' has been created.")

def index(request):
    # additional_training()
    # unique_characters()
    # SmallImg.objects.all().delete()
    # make_csv()
    return render(request, 'index.html')

def start_training(request):
    if request.method == 'POST':
        form = EditAndCheckForm(request.POST)
        if form.is_valid():
            # Process the form data
            edited_text = form.cleaned_data['text_input']
            is_checked = form.cleaned_data['checkbox']
            unrecognizable = form.cleaned_data['unrecognizable']
            record_id = request.POST.get('record_id')
            record = SmallImg.objects.get(id=record_id)
            record.user_content = edited_text
            record.checked = is_checked
            record.unrecognizable = unrecognizable
            record.save()
    else:
        form = EditAndCheckForm()

    queryset = SmallImg.objects.filter(checked=False)
    print(len(queryset))
    record = queryset.first()
    # print(record.parent_pic)

    filter_condition = Q(unrecognizable=False) & Q(checked=True) 
    records = SmallImg.objects.filter(filter_condition)
    total = 0
    misstakes = 0
    for rec in records:
        total = total + len(rec.user_content)
        if not rec.content == rec.user_content:
            distance = Levenshtein.distance(rec.user_content, rec.content)
            misstakes = misstakes + distance
            # print(rec.content, rec.user_content)
    if total > 0:
        percentage = misstakes * 100 / total
        formatted_percentage = "{:.3f}".format(percentage)
        str1 = 'Total processed characters: ' + str(total) + ', misstakes: ' + str(misstakes) +  '; --- misstakes in %: ' + formatted_percentage
        print(str1)
    else:
        str1 = "I don't have picture in database"

    data = {
        'statistic' : str1,
        'total' : len(queryset),
        'record' : record,
        'form' : form
    }
    # print(data)
    return render(request, 'start_training.html', {'data': data})


def logout_view(request):
    logout(request)
    return redirect('index') 

class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'training/login.html'

    def get_success_url(self):
        return reverse_lazy('index')

