from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    core
)

class Ec2WithAppStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Use the default VPC 
        vpc = ec2.Vpc.from_lookup(self, "DefaultVpc", is_default=True)

        # Import existing IAM role by name
        role = iam.Role.from_role_name(
            self,
            "ImportedInstanceRole",
            role_name="steinalytics_role"   # <-- replace with your actual role name
        )

        # Amazon Linux 2 AMI
        ami = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
        )

        # User Data script
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "yum update -y",
            "yum install -y python3 git",
            "cd /home/ec2-user",
            "git clone --depth 1 https://github.com/Siyabongahenry/SteinalyticsReportAPI.git SteinalyticsReportAPI",
            "cd SteinalyticsReportAPI",
            "pip3 install -r requirements.txt",
            "echo '[Unit]' > /etc/systemd/system/fastapi.service",
            "echo 'Description=FastAPI Uvicorn service' >> /etc/systemd/system/fastapi.service",
            "echo '[Service]' >> /etc/systemd/system/fastapi.service",
            "echo 'WorkingDirectory=/home/ec2-user/SteinalyticsReportAPI' >> /etc/systemd/system/fastapi.service",
            "echo 'ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000' >> /etc/systemd/system/fastapi.service",
            "echo 'Restart=always' >> /etc/systemd/system/fastapi.service",
            "echo '[Install]' >> /etc/systemd/system/fastapi.service",
            "echo 'WantedBy=multi-user.target' >> /etc/systemd/system/fastapi.service",
            "systemctl daemon-reload",
            "systemctl enable fastapi.service",
            "systemctl start fastapi.service"
        )

        # EC2 Instance
        ec2.Instance(
            self, "SteinalytcsService",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ami,
            vpc=vpc,
            role=role,  # <-- use the imported role here
            user_data=user_data
        )
