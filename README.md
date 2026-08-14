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

```bash
cd infra
terraform init
terraform apply -var="db_password=<your-password>"
```

Terraform prints the ALB's public DNS name (`alb_dns_name`) once complete --
open it in a browser to see the app. First boot takes 2-3 minutes while the
instance installs Python and starts the app.

## Destroy (avoid ongoing charges)

```bash
cd infra
terraform destroy -var="db_password=<your-password>"
```

NAT Gateway and RDS bill hourly from the moment they're created -- don't leave
this running between work sessions.

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
