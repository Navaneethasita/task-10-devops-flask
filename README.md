This is a real DevOps engineer–level project.
Requirements:

✅ Jenkins CI/CD

✅ Flask app

✅ Docker file (secure, non-root, multistage)

✅ Kubernetes on EC2

✅ Helm deployment

✅ Prometheus + Grafana monitoring

✅ Secure secrets

Developer → Git Push → Jenkins (EC2)
                         ↓
                    Build Docker Image
                         ↓
                    Trivy Scan
                         ↓
                    Push to DockerHub
                         ↓
                    Deploy via Helm
                         ↓
                    Kubernetes Cluster (EC2)
                         ↓
              Prometheus + Grafana Monitoring
			  
🔹 STEP 1 – Infrastructure Setup (EC2)

🖥️ EC2 → Jenkins Server

*Install Docker

1️⃣ Update the System
sudo dnf update -y
2️⃣ Install Docker
sudo dnf install docker -y
3️⃣ Start Docker Service
sudo systemctl enable docker
sudo systemctl start docker

Check status:
sudo systemctl status docker
It should show:
active (running)

*Install Jenkins

sudo yum update –y
sudo wget -O /etc/yum.repos.d/jenkins.repo \
    https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
sudo yum upgrade
sudo sudo dnf install java-17-amazon-corretto -y
sudo yum install jenkins -y
sudo systemctl enable jenkins
sudo systemctl start jenkins

*Install Trivy

1️⃣ Install Required Packages
sudo dnf install -y wget rpm
2️⃣ Add Trivy Repository
sudo rpm --import https://aquasecurity.github.io/trivy-repo/rpm/public.key
sudo wget -O /etc/yum.repos.d/trivy.repo \
https://aquasecurity.github.io/trivy-repo/rpm/trivy.repo
3️⃣ Install Trivy
sudo dnf install trivy -y
4️⃣ Verify Installation
trivy --version

You should see something like:

Version: 0.x.x
🧪 Test Trivy (Very Important)

Test by scanning a public image:

trivy image nginx:latest

It will:

Download vulnerability DB (first time takes 1–2 mins)
Show vulnerabilities grouped by severity


*Install kubectl

before creating cluster we need generic kubectl

pre-req:
✅ Fix kubectl Installation (Correct Method)

Since you're using EKS, install the official way:

🔹 Step 1: Remove wrong file
sudo rm -f /usr/local/bin/kubectl
🔹 Step 2: Download correct kubectl

Run this (recommended official method):

curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
🔹 Step 3: Make it executable
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
🔹 Step 4: Verify
kubectl version --client
You should see something like:

Client Version: v1.29.x
✅ Then Configure Cluster
aws eks update-kubeconfig --region ap-south-1 --name flask-cluster
kubectl get nodes

Create EKS Cluster

*Install eksctl:

curl -sLO https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_Linux_amd64.tar.gz
tar -xzf eksctl_Linux_amd64.tar.gz
sudo mv eksctl /usr/local/bin

To create clusters in aws, we need permissions - so configure aws.
Install AWS CLI locally:

aws configure
create keys from aws security credentials->create access keys

*Create cluster:

eksctl create cluster \
--name flask-cluster \
--region ap-south-1 \
--node-type t3.medium \
--nodes 2

(Wait 10–15 minutes)	 - failed as t3.medium is removed in free tiier account

so try this

eksctl create cluster \
  --name flask-cluster \
  --region ap-south-1 \
  --nodegroup-name ng-1 \
  --node-type m7i-flex.large \
  --nodes 1

*Install Helm

curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

Test:
helm version

🔹 STEP 9 – Prepare Helm Chart

On Jenkins server:

helm create flask-chart - this command creates a Helm chart template structure for your Kubernetes app  
flask-chart/
  Chart.yaml
  values.yaml
  charts/
  templates/
      deployment.yaml
      service.yaml
      ingress.yaml
      serviceaccount.yaml
      _helpers.tpl
      tests/
			
Modify:

values.yaml
image:
  repository: <dockerhubrepo>
  tag: latest

resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"
	
🧠 Add Health Endpoint in Flask

In app.py:

@app.route("/health")
def health():
    return "OK", 200

🔹 STEP 5 – Secrets Management

Create Kubernetes secret:

kubectl create secret generic flask-secret \
  --from-literal=DB_PASSWORD=yourpassword


✅ FIX — Add Docker Hub Credentials in Jenkins
Step 1 — Open Jenkins UI

Go to:

http://<EC2_PUBLIC_IP>:8080
Step 2 — Add Credentials

Manage Jenkins

Manage Credentials

Click (global)

Click Add Credentials

Step 3 — Fill Details

Kind: Username with password

Username: navaneetha4

Password: (Your Docker Hub password OR access token)

ID: dockerhub-creds ← ⚠ MUST match Jenkinsfile

Description: Docker Hub Login

Click Save

Also add aws credentials in jenkins

🌐 STEP 11 – Expose Application

Edit service.yaml in Helm:

type: LoadBalancer

Deploy again.

Get external IP:

kubectl get svc

Access via browser.


📊 STEP 12 – Basic Monitoring

Install Prometheus:

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack


sudo yum update -y
sudo yum install python3 -y
sudo python3 -m ensurepip --upgrade

Add to Flask:

python3 -m pip install prometheus-flask-exporter

In app:

from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app)
	

----DONE----------

MONITORING NOW

Last step:

eksctl delete cluster --name flask-cluster --region ap-south-1



