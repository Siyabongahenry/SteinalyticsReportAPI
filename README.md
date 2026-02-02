# Steinalytics Backend

![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![AWS](https://img.shields.io/badge/AWS-ECR%20%7C%20EC2-orange)

A **FastAPI** project designed to automate Excel report generation and management.  
This backend service integrates with **AWS Cognito** for authorization and communicates with the frontend project **steinalytics-frontend** (ReactJS).

---

## ✨ Features
- FastAPI backend for Excel report automation  
- AWS Cognito authentication (token received via frontend)  
- Dockerized deployment with AWS ECR support  
- Flexible hosting options: EC2 + Nginx + Elastic IP or AMI for autoscaling  
- Virtual environment (venv) support for local development  

---

## ⚙️ Python Version Support
- **Recommended:** Python 3.10 and above (especially for Amazon Linux 2023)  
- **Supported:** Python 3.9 syntax is compatible, but use 3.10+ for production deployments  

---

## 🛠️ Getting Started

### Prerequisites
- Python 3.10+ (3.9 supported for syntax compatibility)  
- Virtual environment (`venv`)  
- Docker & Docker Compose  
- AWS CLI configured with appropriate permissions  

---

### 🔧 Local Development


# 1. Clone the repository
```bash
git clone https://github.com/Siyabongahenry/SteinalyticsReportAPI.git
cd SteinalyticsReportAPI

# 2. Create and activate a virtual environment
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create environment variable file and .gitignore
# Linux/macOS
sudo nano .env
sudo nano .gitignore

# Windows
notepad .env
notepad .gitignore

# Example environment variables
REGION=us-east-1
CORE_ORIGINS=https://www.youdomain.com, https://youdomain.com, https://www.youdomain.co.za
STORAGE_BACKEND=local
BUCKET_NAME=my-upload
OIDC_ISSUER="Your OIDC issuer url"
OIDC_AUDIENCE="Your cognito id"
GOOGLE_BOOKS_API_KEY="Your google books API key"
BOOKS_TABLE="Your DynamoDB book table name"
LIBRARY_BUCKET="Your bucket name where your books get stored"

# 5. Run the application
uvicorn app.main:app --reload
---
### 🔧 Docker Deployment

# 1. Build the Docker image
docker build -t steinalytics-img .

# 2. Run the container
docker run --env-file .env --name steilytics-container -p 8000:8000 steinalytics-img
---
### AWS Deployment using ECS

# 1. Create a repository named steinalytics-api in AWS ECR
# 2. Create an IAM user with ECR access policy
# 3. Authenticate Docker with ECR
aws ecr get-login-password --region <your-region> \
| docker login --username AWS --password-stdin <account-id>.dkr.ecr.<your-region>.amazonaws.com

# 4. Tag and push the image
docker tag steinalytics-img:latest <account-id>.dkr.ecr.<your-region>.amazonaws.com/steinalytics-img:latest
docker push <account-id>.dkr.ecr.<your-region>.amazonaws.com/steinalytics-img:latest

### Running ECS Tasks
# 1. Ensure your .env file is stored securely in Amazon S3 for ECS tasks.
# 2. Configure ECS task definitions to load environment variables from S3.
# 3. Use the pushed image from ECR in your ECS task definition.
# 4. Set the container port to 8000 and protocol to TCP.
---
### Running on only one Amazon EC2 (Amazon Linux 2023)

# 1. Update the EC2 instance
sudo yum update -y

# 2. Switch to ec2-user and clone the repository
cd /home/ec2-user
git clone https://github.com/Siyabongahenry/SteinalyticsReportAPI.git
cd SteinalyticsReportAPI

# 3. Set up Python environment
sudo yum install python3.10 -y
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Create a systemd service for FastAPI
sudo nano /etc/systemd/system/steinalytics.service

# Add the following content:
[Unit]
Description=Steinalytics FastAPI Service
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/SteinalyticsReportAPI
ExecStart=/home/ec2-user/SteinalyticsReportAPI/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target

# Save and enable service
sudo systemctl daemon-reload
sudo systemctl enable steinalytics.service
sudo systemctl start steinalytics.service

# 5. Install and configure Nginx
sudo yum install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx

# Configure reverse proxy
sudo nano /etc/nginx/conf.d/steinalytics.conf

# Add the following:
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Test and reload Nginx
sudo nginx -t
sudo systemctl restart nginx

# 6. Attach a static IP (Elastic IP)
# - Allocate an Elastic IP in AWS
# - Associate it with your EC2 instance

# 7. Configure Security Groups
# - Allow inbound traffic on port 80 (HTTP) from anywhere (0.0.0.0/0)
# - Optionally allow port 443 (HTTPS) if you plan to add SSL/TLS

# 8. Update DNS records
# Point your domain’s A record to the Elastic IP
# Example:
# yourdomain.com   A   <Elastic-IP>
# www.yourdomain.com   A   <Elastic-IP>

---
### ⚙️ Running with EC2 + Load Balancer + Auto Scaling (Amazon Linux 2023)

# 1. Create a Security Group
# - Allow inbound traffic on port 80 (HTTP) and 443 (HTTPS) from the internet (0.0.0.0/0) (to be attached to load balancer)
# - Create another security group for EC2 instances that allows inbound traffic on port 8000 only from the Load Balancer security group - to be attached to ec2 instance.

# 2. Create an IAM Role for EC2
# - Go to IAM → Roles → Create Role.
# - Select EC2 as the trusted entity.
# - Attach policies for S3 and Dynamodb.
# - To be attached to your ec2 instnance.

# 3. Launch an EC2 Instance (to prepare AMI)
sudo yum update -y
cd /home/ec2-user
git clone https://github.com/Siyabongahenry/SteinalyticsReportAPI.git
cd SteinalyticsReportAPI

# Install Python and dependencies
sudo yum install python3.10 -y
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create a systemd service for FastAPI (skip Nginx since Load Balancer will handle traffic)
sudo nano /etc/systemd/system/steinalytics.service

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/SteinalyticsReportAPI
ExecStart=/home/ec2-user/SteinalyticsReportAPI/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable steinalytics.service
sudo systemctl start steinalytics.service

# 4. Create an AMI (Amazon Machine Image)
# - From the EC2 console, select your configured instance.
# - Choose "Create Image" to generate an AMI that includes your app and service setup.

# 5. Create a Launch Template
# - Use the AMI created above.
# - Attach the IAM role created earlier.
# - Assign the EC2 security group that allows inbound traffic from the Load Balancer SG on port 8000.

# 6. Create an Auto Scaling Group
# - Based on the launch template.
# - Configure desired capacity, min/max instances.
# - Attach the Auto Scaling Group to a Target Group.

# 7. Create a Target Group
# - Protocol: HTTP
# - Port: 8000
# - Target type: Instance
# - Health checks: HTTP on port 8000

# 8. Create a Load Balancer
# - Application Load Balancer (ALB).
# - Listener ports: 80 (HTTP) and/or 443 (HTTPS).
# - Attach the Load Balancer security group (allows inbound from internet).
# - Forward traffic to the Target Group (port 8000).

# 9. Update DNS Records
# - Point your domain’s A record to the Load Balancer DNS name.
# Example:
# yourdomain.com   A   <Load-Balancer-DNS>
# www.yourdomain.com   A   <Load-Balancer-DNS>

# ✅ Your FastAPI app now runs behind a Load Balancer with Auto Scaling.

















