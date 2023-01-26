import os
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(5, 10) # seconds

    @task()
    def wado(self):       
        bearer_token = os.getenv('bearer_token')

        headers = {'Accept':'multipart/related; type="application/dicom"; transfer-syntax=*', "Authorization":bearer_token}
        study_instance_uid = ''
        series_instance_uid = ''
        sop_instance_uid = ''
        url = f'/v1/studies/{study_instance_uid}/series/{series_instance_uid}/instances/{sop_instance_uid}'
        self.client.get(url, headers=headers)

