from locust import HttpUser, task, between
from io import BytesIO
import pydicom
import gc
import requests


from urllib3.filepost import encode_multipart_formdata, choose_boundary
def encode_multipart_related(fields, boundary=None):
    if boundary is None:
        boundary = choose_boundary()

    body, _ = encode_multipart_formdata(fields, boundary)
    content_type = str('multipart/related; boundary=%s' % boundary)

    return body, content_type

class APIUser(HttpUser):
    wait_time = between(5, 10) # seconds

    @task()
    def stow(self):       
        bearer_token = ''
        sas_token = ''
        test_file_1mb = '' + sas_token
        resp = requests.get(test_file_20mb)
        dcm = pydicom.dcmread(BytesIO(resp.content))
        dcm.SOPInstanceUID = pydicom.uid.generate_uid()
        
        dicom_file_bytes = BytesIO()
        dcm.save_as(dicom_file_bytes)

         # Free up memory by deleting dcm
        del dcm
        gc.collect()

        files = {'file': ('dicomfile', dicom_file_bytes, 'application/dicom')}
        body, content_type = encode_multipart_related(fields = files)
        headers = {'Accept':'application/dicom+json', "Content-Type":content_type, "Authorization":bearer_token} 
        self.client.post(f"/v1/studies", body, headers=headers)

    @task()
    def wado(self):       
        bearer_token = ''

        headers = {'Accept':'multipart/related; type="application/dicom"; transfer-syntax=*', "Authorization":bearer_token}
        url_50kb = f'/v1/studies/1.3.6.1.4.1.14519.5.2.1.7009.2403.127167041981135647798070870953/series/1.3.6.1.4.1.14519.5.2.1.7009.2403.932967614838729723558638723245/instances/2.25.199379631607793098254684776023203372023'
        url_500kb = f'/v1/studies/1.3.6.1.4.1.14519.5.2.1.7009.2403.581744258226084463500999666522/series/1.3.6.1.4.1.14519.5.2.1.7009.2403.933485081908156148510622788853/instances/2.25.183640465096328981184599285604598805684'
        url_50mb = f'/v1/studies/2.25.21998882328480231931247820891791488411/series/2.25.78003528804982655290598581495266807423/instances/2.25.73000370295695537871846720908485297353'
        url_1mb = f'/v1/studies/2.25.315309600499708483063757878757019203783/series/2.25.19250090535806010342750305058852963515/instances/2.25.286772014167999407424202068240090470408'
        url_2mb = f'/v1/studies/2.25.315309600499708483063757878757019203783/series/2.25.19250090535806010342750305058852963515/instances/2.25.154592351352186231378529821422964909548'
        url_5mb = f'/v1/studies/2.25.328590396843593697573804982446951364485/series/2.25.253355217560141298487759131978518586236/instances/2.25.53014649691333312088432379113110971409'
        url_10mb = f'/v1/studies/2.25.104077233594482102790898941867164809827/series/2.25.73497156253124667107844157755906824095/instances/2.25.231251571594562196034516522276417294600'
        url_20mb = f'/v1/studies/2.25.235527517288144631163561160489044426722/series/2.25.251305243035330646718593259684188357039/instances/2.25.200712961383449909686886443824398847845'
        self.client.get(url_1mb, headers=headers)

