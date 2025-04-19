# GitHub Pull Request Creation Module

terraform {
  required_providers {
    github = {
      source  = "integrations/github"
      version = ">= 5.0.0"
    }
  }
  required_version = ">= 1.8.0"
}

provider "github" {}
