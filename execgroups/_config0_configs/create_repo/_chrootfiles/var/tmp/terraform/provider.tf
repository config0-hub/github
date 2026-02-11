# GitHub repository configuration
# This Terraform configuration creates a GitHub repository with specified settings

terraform {
  required_providers {
    github = {
      source = "integrations/github"
      # Specify version constraint for better compatibility
      version = "~> 5.0"
    }
  }
}

provider "github" {}