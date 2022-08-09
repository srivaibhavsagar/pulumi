import sys
import json
import os
import pulumi
from pulumi import automation as auto
from pulumi_aws import s3

import pulumi_aws as aws
from pulumi import ResourceOptions


# This is the pulumi program in "inline function" form
def pulumi_program():
    # IMPORTANT: Python appends an underscore (`import_`) to avoid conflicting with the keyword.


    group = aws.ec2.SecurityGroup('my-sg',
        name='launch-wizard-2',
        description='launch-wizard-2 created 2022-02-18T22:21:22.537+00:00',
        opts=ResourceOptions(import_='sg-011ff0e73b9c45cfb'))
    
    web = aws.ec2.Instance("pulumi-imports",
    ami='ami-0e34bbddc66def5ac',
    instance_type='t2.micro',
    tags={
        "Name": "pulumi-import",
    },
    opts=ResourceOptions(import_='i-0bdcefd5abf5c784c'))

# To destroy our program, we can run python main.py destroy
destroy = False
args = sys.argv[1:]
if len(args) > 0:
    if args[0] == "destroy":
        destroy = True

project_name = "inline_s3_project"
# We use a simple stack name here, but recommend using auto.fully_qualified_stack_name for maximum specificity.
stack_name = "dev"
# stack_name = auto.fully_qualified_stack_name("myOrgOrUser", project_name, stack_name)

# Specify a local backend instead of using the service.
project_settings=auto.ProjectSettings(
    name=project_name,
    runtime="python",
    backend={"url": "s3://my-bucket-8ff2384"})

secrets_provider = "awskms://aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee?region=us-west-2"
# kms_env = os.environ.get("KMS_KEY")
kms_env = "cf305f60-1fac-414b-b0f5-6b975d66725a"

if kms_env:
    secrets_provider = f"awskms://{kms_env}?region=eu-west-2"
if secrets_provider == "awskms://aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee?region=us-west-2":
    raise Exception("Please provide an actual KMS key for secrets_provider")

stack_settings=auto.StackSettings(
    secrets_provider=secrets_provider)

# create or select a stack matching the specified name and project.
# this will set up a workspace with everything necessary to run our inline program (pulumi_program)
stack = auto.create_or_select_stack(stack_name=stack_name,
                                    project_name=project_name,
                                    program=pulumi_program,
                                    opts=auto.LocalWorkspaceOptions(project_settings=project_settings,
                                                                    secrets_provider=secrets_provider,
                                                                    stack_settings={"dev": stack_settings}))

print("successfully initialized stack")

# for inline programs, we must manage plugins ourselves
print("installing plugins...")
stack.workspace.install_plugin("aws", "v4.0.0")
print("plugins installed")

# set stack configuration specifying the AWS region to deploy
print("setting up config")
stack.set_config("aws:region", auto.ConfigValue(value="eu-west-2"))
print("config set")

print("refreshing stack...")
stack.refresh(on_output=print)
print("refresh complete")

if destroy:
    print("destroying stack...")
    stack.destroy(on_output=print)
    print("stack destroy complete")
    sys.exit()

print("updating stack...")
up_res = stack.up(on_output=print)
print(f"update summary: \n{json.dumps(up_res.summary.resource_changes, indent=4)}")
# print(f"website url: {up_res.outputs['website_url'].value}")