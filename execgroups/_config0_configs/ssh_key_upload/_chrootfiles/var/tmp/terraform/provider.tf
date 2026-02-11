# GitHub Deploy Key Configuration
# This module creates a deploy key for a GitHub repository

terraform {
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.8.0"
}

provider "github" {
}
