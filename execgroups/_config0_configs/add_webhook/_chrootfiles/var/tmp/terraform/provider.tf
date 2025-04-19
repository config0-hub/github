# GitHub webhook configuration
# This module creates a GitHub repository webhook

terraform {
  # Minimum required OpenTofu version
  required_version = ">= 1.8.0"

  required_providers {
    github = {
      source = "integrations/github"
      # Use a specific version or constraint for stability
      version = ">= 5.0.0"
    }
  }
}

provider "github" {}
