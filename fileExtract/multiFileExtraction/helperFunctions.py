from PyPDF2 import PdfReader
import fitz
import pandas as pd
from bs4 import BeautifulSoup
from inscriptis import get_text
import os, re
import pytesseract
from PIL import Image, ImageSequence
import nltk
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer

##PDF RELATED FUNCTIONS

def check_pdf(loc, page=0):
    reader = PdfReader(loc)
    page = reader.pages[page]
    text = page.extract_text()
    return text

def text_pdf_extraction(loc):
    text_content = []
    reader = PdfReader(loc)
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        text = page.extract_text()
        text_content.append(text + f"_page{i}")
    return text_content

def text_extract_check(text_content, keyword):
    foundList = []
    lines_with_keyword = extract_lines_containing_keyword(text_content, keyword)
    if lines_with_keyword:
        print(f"Lines containing '{keyword}':")
        for line in lines_with_keyword:
            print(line)
            foundList.append(line)
    else:
        print(f"No lines containing '{keyword}' found.")

    return foundList


def extract_lines_containing_keyword(text, keyword):
    lines_with_keyword = []
    
    # Split the text into lines
    lines = text.splitlines()
    
    # Iterate through the lines to find the ones containing the keyword
    for line in lines:
        if keyword.lower() in line.lower():
            lines_with_keyword.append(line)
    
    return lines_with_keyword

def pdf_image_extraction(loc):
    imgList = []
    doc = fitz.Document(loc)
    for i in range(len(doc)):
        page = doc[i]
        xref = page.get_images()[0][0]
        baseImage = doc.extract_image(xref)
        imgList.append(baseImage)
       
    return imgList


def updatecsv(data_dict, key):
    if key == "bus":
        df = pd.read_csv(os.getcwd()+os.sep+"multiFileExtraction"+os.sep+"bus_priority_all_data.csv")

        df['BUS PRIORITY'] = df.apply(lambda row: data_dict.get(row['siteno'][:4], {}).get('detectedImgList') or data_dict.get(row['siteno'][:4], {}).get('detectedTextList') or row['BUS PRIORITY'], axis=1)

    if key == "tram":
        df = pd.read_csv(os.getcwd()+os.sep+"multiFileExtraction"+os.sep+"tram_priority_all_data.csv")

        df['TRAM PRIORITY'] = df.apply(lambda row: data_dict.get(row['siteno'][:4], {}).get('detectedImgList') or data_dict.get(row['siteno'][:4], {}).get('detectedTextList') or row['TRAM PRIORITY'], axis=1)

    if key == "bicycle":
        df = pd.read_csv(os.getcwd()+os.sep+"multiFileExtraction"+os.sep+"bicycle_priority_all_data.csv")

        df['BICYCLE PRIORITY'] = df.apply(lambda row: data_dict.get(row['siteno'][:4], {}).get('detectedImgList') or data_dict.get(row['siteno'][:4], {}).get('detectedTextList') or row['BICYCLE PRIORITY'], axis=1)

## TIF RELATED FUNCTIONS
def read_text_from_image(image_path):
    # Open the image using Pillow
    image = Image.open(image_path)

    # Initialize an empty string to store all extracted text
    all_extracted_text = ""

    # Iterate through all pages in the TIF file
    for index, page in enumerate(ImageSequence.Iterator(image)):
        # Extract text from the current page using pytesseract
        extracted_text = pytesseract.image_to_string(page)

        # Add the extracted text to the all_extracted_text variable
        all_extracted_text += f"Page {index + 1}:\n{extracted_text}\n\n"

    return all_extracted_text

##HTML RELATED FUNCTIONS
def lemmatize_keyword(keyword):
    #lemmatize keyword to its original form
    lemmatizer = WordNetLemmatizer()
    lemma_keyword = lemmatizer.lemmatize(keyword)
    #generate a pattern that covers different word forms and variations of the keyword
    pattern = re.compile(r"\b" + re.escape(lemma_keyword) + r"(\w*)\b", re.IGNORECASE)
    return lemma_keyword, pattern

def get_max_tab_number(child_folder_path):
    max_tab = 0
    for file_name in os.listdir(child_folder_path):
        if file_name.endswith("tabstrip.htm"):
            tabstrip_file = os.path.join(child_folder_path, file_name)
            with open(tabstrip_file, "r", encoding="ISO-8859-1") as f:
                soup = BeautifulSoup(f, "html.parser")
                for a_tag in soup.find_all("a", href=True):
                    href = a_tag.get("href")
                    if href.startswith("sheet") and href.endswith(".htm"):
                        sheet_number = int(href[5:-4])
                        if sheet_number > max_tab:
                            max_tab = sheet_number
    return max_tab




def extract_text_from_html_text(folder_path, keyword):
    lemma_keyword, pattern = lemmatize_keyword(keyword)

    keywords = ["DATE", "SITE", "MUNICIPALITY"]
    data = {}
    found_files = []

    for dirpath, dirnames, filenames in os.walk(folder_path):
         max_tab = get_max_tab_number(dirpath)
         for file in filenames:
          if file.startswith('sheet') and file.lower().endswith(('.htm')):
              file_dict = {}
              parent_folder = os.path.basename(dirpath)
              if "_files" in parent_folder.lower():
                    parent_folder = parent_folder[:-6]
              new_filename = f"{parent_folder}_{file}"
              sheet_number = int(file.split('sheet')[1][:3])
              if sheet_number >= 1 and sheet_number <= max_tab:
                  file_path = os.path.join(os.path.join(dirpath, file))
                  with open(file_path, "r", encoding="ISO-8859-1") as f:
                            soup = BeautifulSoup(f, "html.parser")
                            tags = soup.find_all(string=pattern)
                            sentences = []
                            if tags:
                              for tag in tags:
                                  tag_text = tag.get_text().strip().replace('\n', '')
                                  tag_text = ' '.join(filter(None, tag_text.split(' ')))
                                  if tag_text:
                                      sentences.append(tag_text)
                              if sentences:
                                  sheet_file = 'sheet001.htm'
                                  sheet_path = os.path.join(os.path.join(dirpath, sheet_file))
                                  with open(sheet_path, "r", encoding="ISO-8859-1") as f:
                                      html_content = f.read()
                                  soup = BeautifulSoup(html_content, "html.parser")
                                  # Find the <tr> tags in the HTML file
                                  trs = soup.find_all("tr")
                                  # Loop through each <tr> tag
                                  for tr in trs:
                                  # Find the <td> tags in the <tr> tag
                                      tds = tr.find_all("td")
                                      # Loop through each <td> tag
                                      for i, td in enumerate(tds):
                                      # Check if the text in the <td> tag matches any of the keywords
                                        if td.text.strip() in keywords:
                                      # If a keyword is found, get the text of the next <td> tag
                                            next_td = None
                                            if i+1 < len(tds):
                                                next_td = tds[i+1]
                                            elif i+2 < len(tds):
                                                next_td = tds[i+2]
                                            if next_td:
                                            # Check if the text of the next <td> tag is empty
                                              if next_td.text.strip() == '':
                                            # If the text of the next <td> tag is empty, get the text of the next <td> tag after it
                                                  if i+2 < len(tds):
                                                    next_td = tds[i+2]
                                            data[td.text.strip()] = next_td.text.strip()
                                  for keyword in keywords:
                                      file_dict[keyword] = data.get(keyword, 'Not found')
                                  file_dict.update({
                                          "OPSHEET ID": new_filename,
                                          "DATE": data.get("DATE", "Not found"),
                                          "SITE": data.get("SITE", "Not found"),
                                          "SITE NO.": parent_folder,
                                          "MUNICIPALITY": data.get("MUNICIPALITY", "Not found"),
                                          "BUS PRIORITY": sentences 
                                          })
                                  found_files.append(file_dict)
                                  print("OPSHEET ID:", new_filename)
                                  for keyword in keywords:
                                      print(f"{keyword}: {data.get(keyword, 'Not found')}")
                                  print("SITE NO.:", parent_folder)
                                  print(f"BUS PRIORITY: {sentences}")
                                  print("-------------")
                              else:
                                  print("OPSHEET ID:", new_filename)
                                  print(f"BUS PRIORITY:" "NO BUS FOUND")
                                  print("-------------")             
   
    if not found_files:
        print(f"No file with keyword '{keyword}' was found in {folder_path}.")
    else: 
        return found_files