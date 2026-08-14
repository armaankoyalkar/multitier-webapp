# Multi-Tier Web Application on AWS

Design and deployment of a highly available, multi-tier web application on AWS,
built with a custom VPC, an Application Load Balancer, an EC2 Auto Scaling Group,
and an RDS MySQL database. See `plan.md` for the full design rationale, phase-by-
phase build plan, and architecture diagram.

## Stack
- **Infrastructure:** Terraform (AWS provider `~> 5.0`)
- **App tier:** Python 3, Flask, Gunicorn -- runs as a systemd service on port 5000
- **Data tier:** Amazon RDS (MySQL 8.0), private subnet only

## Prerequisites
- An AWS account with the CLI configured (`aws configure`)
- [Terraform](https://developer.hashicorp.com/terraform/downloads) >= 1.5
- Enough EC2 vCPU quota for `asg_max_size` x vCPUs-per-instance (see **Known
  issues** below -- this matters more than it sounds like it should)

## Deploy

Prerequisites (one-time, on your own machine)
bash
sudo apt-get update && sudo apt-get install -y gnupg software-properties-common
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt-get update && sudo apt-get install terraform
aws configure

Enter your new account's access key, secret key, and region (ap-south-1 is the default baked into the files — change it in variables.tf if you're using a different region).

Step-by-step

1. Unzip and enter the infra folder

bash
unzip project-root.zip && cd project-root/infra

2. Initialize Terraform

bash
terraform init

Downloads the AWS provider. One-time step.

3. Review the plan

bash
terraform plan -var="db_password=<choose-a-strong-password>"

Read through this — it lists every resource about to be created: VPC, 6 subnets, IGW, NAT Gateway, 3 route table associations sets, 3 security groups, RDS instance, launch template, ALB, target group, listener, ASG, scaling policy. Roughly 30+ resources total. Nothing is created yet at this step.

4. Apply

bash
terraform apply -var="db_password=<same-password>"

Type yes when prompted. This takes 5–10 minutes, mostly waiting on RDS to finish provisioning — that's normal, don't interrupt it.

5. Get the ALB URL

bash
terraform output alb_dns_name

Open that in a browser. Give it 2–3 minutes after the resources finish creating for the EC2 instances to boot and run their user-data script (installing Python, Flask, Gunicorn) before the app responds.

6. Test it properly

Load the ALB URL, add/complete/delete a task
Refresh several times — with asg_desired_capacity = 2 now, you should genuinely see the "Served by instance" ID alternate between two different instance IDs, proving the ALB is load-balancing across real, separate instances (not just one, like before)
In the EC2 console, manually terminate one of the two running instances — watch the ASG launch a replacement automatically within a minute or two
Try connecting to the RDS endpoint from your laptop with a MySQL client — confirm it times out

7. Capture your Round 2 evidence
Same checklist as before — VPC resource map, ALB loading the app, healthy targets, ASG showing running instances, RDS "not publicly accessible."

8. Tear down when you're done for the day

bash
terraform destroy -var="db_password=<same-password>"

NAT Gateway and RDS bill hourly regardless of whether you're actively using them — don't leave this running overnight unless you mean to.

## Project structure

```
project-root/
├── infra/                   <- Terraform
│   ├── vpc.tf                 VPC, subnets, IGW, NAT Gateway, route tables
│   ├── security_groups.tf     ALB / EC2 / RDS security groups
│   ├── alb.tf                 Load balancer, target group, listener
│   ├── asg.tf                 Launch template, IAM role, Auto Scaling Group
│   ├── rds.tf                 RDS MySQL instance + subnet group
│   └── variables.tf           All configurable inputs
├── app/
│   └── app.py                Flask task manager (reads DB config from env vars)
├── scripts/
│   └── user-data.sh          EC2 bootstrap script (Terraform template)
├── docs/
│   └── architecture-diagram.png
└── README.md                 <- this file
```
