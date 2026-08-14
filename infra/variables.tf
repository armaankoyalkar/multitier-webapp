variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name prefix used for tagging and naming all resources"
  type        = string
  default     = "multitier-webapp"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Two Availability Zones to spread subnets across"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for the two public subnets (host the ALB)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_app_subnet_cidrs" {
  description = "CIDR blocks for the two private application subnets (host EC2)"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "private_db_subnet_cidrs" {
  description = "CIDR blocks for the two private database subnets (host RDS)"
  type        = list(string)
  default     = ["10.0.21.0/24", "10.0.22.0/24"]
}

# ---- EC2 / Auto Scaling ----
variable "instance_type" {
  description = "EC2 instance type for the app tier"
  type        = string
  default     = "t3.micro"
}

variable "asg_min_size" {
  description = "Minimum ASG size"
  type        = number
  default     = 2
}

variable "asg_max_size" {
  description = "Maximum ASG size"
  type        = number
  default     = 4
}

variable "asg_desired_capacity" {
  description = "Desired ASG size"
  type        = number
  default     = 2
}

# ---- RDS ----
variable "db_engine_version" {
  description = "MySQL engine version for RDS"
  type        = string
  default     = "8.0"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_multi_az" {
  description = "Enable RDS Multi-AZ (adds cost; leave false for a demo/mini-project)"
  type        = bool
  default     = false
}

variable "db_name" {
  description = "Initial database name"
  type        = string
  default     = "appdb"
}

variable "db_username" {
  description = "Master username for RDS"
  type        = string
  default     = "admin"
}

variable "db_password" {
  description = "Master password for RDS. Pass via -var, terraform.tfvars (gitignored), or the TF_VAR_db_password environment variable. Never commit a real value."
  type        = string
  sensitive   = true
}
