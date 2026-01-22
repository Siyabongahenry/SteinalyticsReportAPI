from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    core
)

class Ec2WithAppStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, "DefaultVpc", is_default=True)

        role = iam.Role.from_role_name(
            self,
            "ImportedInstanceRole",
            role_name="steinalytics_role"
        )

        ami = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
        )

        # Load external user_data.sh and inject variables
        with open("scripts/user_data.sh") as f:
            script = f.read()

        user_data = ec2.UserData.for_linux()
        user_data.add_commands(script)

        # Pass environment variables into User Data
        user_data.add_commands(
            f"export REPO_URL=https://github.com/Siyabongahenry/SteinalyticsReportAPI.git",
            f"export BRANCH=main",
            f"export APP_DIR=SteinalyticsReportAPI"
        )

        ec2.Instance(
            self, "SteinalytcsService",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ami,
            vpc=vpc,
            role=role,
            user_data=user_data
        )
