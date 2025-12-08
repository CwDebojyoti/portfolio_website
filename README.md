Step4: Build Docker Image:
docker build -t portfolio-website -f Dockerfile.train .

Step5: Tag the Docker Image locally:
docker tag portfolio-website gcr.io/spheric-crowbar-480612-n9/portfolio-website

Step6: Push the image to Google Cloud Registry:
docker push gcr.io/spheric-crowbar-480612-n9/portfolio-website



Deployment using CloudBuild and establish CI/CD:

To Deploy the Training image and to build CI/CD, CloudBuild service has been used. Job sequence is defined in cloudbuild.yaml file. To trigger deployment using cloudbuild_hpt_train.yaml file the following command has been used:
'gcloud builds submit --config cloudbuild.yaml --project=spheric-crowbar-480612-n9'



gcloud projects add-iam-policy-binding spheric-crowbar-480612-n9 --member="serviceAccount:portfolio@spheric-crowbar-480612-n9.iam.gserviceaccount.com" --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding spheric-crowbar-480612-n9 --member="serviceAccount:portfolio@spheric-crowbar-480612-n9.iam.gserviceaccount.com" --role="roles/iam.serviceAccountUser"


gcloud builds submit --config cloudbuild.yaml --service-account=portfolio@spheric-crowbar-480612-n9.iam.gserviceaccount.com --project=spheric-crowbar-480612-n9
