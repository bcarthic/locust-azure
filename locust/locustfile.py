from locust import HttpUser, task, between
from io import BytesIO
import pydicom
import numpy as np
import requests
import os

from urllib3.filepost import encode_multipart_formdata, choose_boundary
def encode_multipart_related(fields, boundary=None):
    if boundary is None:
        boundary = choose_boundary()

    body, _ = encode_multipart_formdata(fields, boundary)
    content_type = str('multipart/related; boundary=%s' % boundary)

    return body, content_type

def create_dicom_file_as_bytes():
        # Create a new DICOM dataset
        ds = pydicom.Dataset()

        # Set the transfer syntax
        ds.is_little_endian = True
        ds.is_implicit_VR = True

        # Set the various DICOM data elements
        ds.PatientName = "John Doe"
        ds.PatientID = "123456"
        ds.SOPClassUID = pydicom.uid.generate_uid()
        ds.StudyInstanceUID = "1.2.3.4"
        ds.SeriesInstanceUID = pydicom.uid.generate_uid()
        ds.SOPInstanceUID = pydicom.uid.generate_uid()
        ds.SamplesPerPixel = 1
        ds.Rows = 512
        ds.Columns = 512
        ds.BitsAllocated = 8
        ds.BitsStored = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.PhotometricInterpretation = "MONOCHROME2"

        # Create a sample image with random pixel data and set it as the pixel data
        image = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
        ds.PixelData = image.tobytes()

        # Create a BytesIO object
        buffer = BytesIO()
        # Save the dataset to the BytesIO object
        ds.save_as(buffer, write_like_original=False)
        # Get the byte data from the buffer
        dicom_file_bytes = buffer.getvalue()

        return dicom_file_bytes

class APIUser(HttpUser):
    wait_time = between(5, 10) # seconds

    @task()
    def stow(self):       
        
        dicom_file_bytes = create_dicom_file_as_bytes()

        bearer_token = os.getenv('bearer_token')
        files = {'file': ('dicomfile', dicom_file_bytes, 'application/dicom')}
        body, content_type = encode_multipart_related(fields = files)
        headers = {'Accept':'application/dicom+json', "Content-Type":content_type, "Authorization":bearer_token} 
        self.client.post(f"/v1/partitions/Microsoft.Default/studies", body, headers=headers)

    # @task()
    # def changefeed(self):       
    #     bearer_token = os.getenv('bearer_token')

    #     headers = {"Authorization":bearer_token}
    #     url = f'/v1/changefeed'
    #     self.client.get(url, headers=headers)
