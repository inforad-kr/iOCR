import easyocr
from datetime import datetime
import time
import torch

# Set device to CPU


def text_recognition():
    torch.device('cpu')
    time1 = time.time()
    reader = easyocr.Reader(["en"])
    time2 = time.time()
    result = reader.readtext("3.jpg", detail=0)
    time3 = time.time()
    print(time2 - time1)
    print(result)
    print(time3 - time2)
    print()

    time4 = time.time()
    result = reader.readtext("3c.jpg", detail=0)
    time5 = time.time()
    print(result)
    print(time5 - time4)
    print()

    time4 = time.time()
    result = reader.readtext("1.jpg", detail=0)
    time5 = time.time()
    print(result)
    print(time5 - time4)
    print()

    time4 = time.time()
    result = reader.readtext("2.jpg", detail=0)
    time5 = time.time()
    print(result)
    print(time5 - time4)
    print()
    
    return result

def main():

    # file_path = "3.jpg"
    # words_list = text_recognition(file_path=file_path)
    # for el in words_list:
    #     print(el)
    
    # file_path = "3c.jpg"
    # words_list = text_recognition(file_path=file_path)
    # for el in words_list:
    #     print(el)
    text_recognition()

if __name__ == "__main__":
    main()