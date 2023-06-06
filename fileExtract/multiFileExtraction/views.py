import zipfile
import pytesseract
from PIL import Image
from .models import UploadedFile
from django.shortcuts import render
import io, json, os
from django.utils.html import escape
import pandas as pd
from multiFileExtraction.helperFunctions import check_pdf, text_extract_check, text_pdf_extraction, pdf_image_extraction, read_text_from_image

# INITIALIZING TESSERACT.EXE FOR PERFORMING OCR
path_to_tesseract = r"C:\Users\Naveen\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = path_to_tesseract



def home_page(request):
    return render(request, 'Home_page.html')




def upload_file(request):

    detectedTextList = []
    detectedImgList = []
    data_dict = {}
    result = {}
    unzip_folder_path = os.getcwd()+os.sep+"multiFileExtraction"+os.sep+"unzip_data"

    if request.method == 'POST' and request.FILES.getlist('file'):

        files = request.FILES.getlist('file')  # Access uploaded files

        for file in files:
            print(file, "PRINTING FILE")
            # uploaded_file = request.FILES['file']

            # Save the uploaded file to the database
            uploaded = UploadedFile(file=file)
            uploaded.save()

            file_path = uploaded.file.path
            # file_name = os.path.basename(uploaded_file.name)
            file_name = file
            print(file_name, "PRINTING NAME")
            keyword = request.POST.get('keyword')  # Get the selected keyword from the dropdown

        
            if file_path.endswith('.pdf'):
                extracted_text = check_pdf(file_path)
                if extracted_text:
                    text = text_pdf_extraction(file_path)
                    for t in text:
                        detectedTextList = text_extract_check(text_content=t, keyword=keyword)
                        if detectedTextList:
                            if file_name not in data_dict:
                                data_dict[file_name] = {'detectedTextList': []}
                            data_dict[file_name]['detectedTextList'].append(detectedTextList)
                            # data_dict[file_name] = detectedTextList
                        print(detectedTextList)
                        
                else:
                    baseImage = pdf_image_extraction(file_path)
                    for img in baseImage:
                        extracted_text = pytesseract.image_to_string(Image.open(io.BytesIO(img['image'])))
                        detectedImgList = text_extract_check(text_content=extracted_text, keyword=keyword)
                        if detectedImgList:
                            if file_name not in data_dict:
                                data_dict[file_name] = {'detectedImgList': []}
                            data_dict[file_name]['detectedImgList'].append(detectedImgList)
                            # data_dict[file_name] = detectedImgList
                        # print(detectedImgList)


            elif ((file_path.endswith('.tif'))):

                text = read_text_from_image(file)
                lines_with_keyword = text_extract_check(text, keyword)
                if lines_with_keyword:
                    if file_name not in data_dict:
                        data_dict[file_name] = {'detectedImgList': []}
                        data_dict[file_name]['detectedImgList'].append(lines_with_keyword)

            elif (file_path.endswith('.html')):
                return 0
            
            elif (file_path.endswith('.zip')):
                    # Open the zip file
                with zipfile.ZipFile(file_path, "r") as zip_file:
                 # Loop through each file in the zip file
                    for zipped_file in zip_file.namelist():
                        # Extract the file to the output folder
                        zip_file.extract(zipped_file, unzip_folder_path)
        
                print(f"Extracted {file_name} sucessfully!")
                    
        
            
            
            
            
            result = data_dict    
        
        # Pass the result to the template
        return render(request, 'result.html', {'result': result})
    
    return render(request, 'upload.html')


def view_data(request):

    csv_filename = ""

    print("HAIL HITMAN")
    if request.method == 'POST':

        # Handle form submission
        keyword = request.POST.get('dropdown')


        if keyword == 'bus':
            csv_filename = 'bus_priority_all_data.csv'
        elif keyword == 'tram':
            csv_filename = 'bus_priority_all_data.csv'
        elif keyword == 'bicycle':
            csv_filename = 'bus_priority_all_data.csv'

    
    # Read the Map Data CSV file
    df = pd.read_csv(os.getcwd()+os.sep+"multiFileExtraction"+os.sep+"Map_Data.csv")

    # Read the Bus Priority CSV file with siteno values
    
    if csv_filename == "":
        bus_df = pd.read_csv(os.getcwd()+os.sep+"multiFileExtraction"+os.sep+"bus_priority_all_data.csv")
        print(123123123)
    else:
        bus_df = pd.read_csv(os.getcwd()+os.sep+"multiFileExtraction"+os.sep+csv_filename)
        print("rishab is a beast")

    filtered_df = bus_df['SITE NO'].unique().tolist()
    print(len(filtered_df))
    df_filtered_map = df[df['SITE_NO'].isin(filtered_df)]
    print(len(df_filtered_map))


    # Extract latitude and longitude columns
    latitudes = df_filtered_map['LAT'].tolist()
    longitudes = df_filtered_map['LONG'].tolist()
    sitenos = df_filtered_map['SITE_NO'].tolist()
    site_names = df_filtered_map['SITE_NAME'].tolist()

    # Escape and encode site_names as a JSON string
    site_names_json = json.dumps([escape(name) for name in site_names])

    context = {
        'latitude': latitudes,
        'longitude': longitudes,
        'siteno': sitenos,
        'site_names' : site_names_json
    }

    return render(request, 'viewData.html', context)