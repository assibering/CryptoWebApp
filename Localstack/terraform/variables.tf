variable "aws_access_key_ID" {
description = "AWS Access Key ID"
type        = string
default     = "test"
}

variable "aws_secret_access_key" {
description = "AWS Secret Access Key"
type        = string
default     = "test"
}

variable "aws_default_region" {
description = "AWS Default Region"
type        = string
default     = "us-east-1"
}

variable "environment" {
description = "Deployment environment"
type        = string
default     = "local"
}

variable "aws_endpoint" {
description = "AWS endpoint URL"
type        = string
default     = "http://localhost:4566"
}
