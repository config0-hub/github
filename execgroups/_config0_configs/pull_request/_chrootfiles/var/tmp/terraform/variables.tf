variable "repository" {
  description = "The name of the GitHub repository where the PR will be created"
  type        = string
  default     = "private-test"
}

variable "base_branch" {
  description = "The target branch for the pull request (where changes will be merged into)"
  type        = string
  default     = "main"
}

variable "feature_branch" {
  description = "The source branch for the pull request (containing the changes to be merged)"
  type        = string
  default     = "dev"
}

variable "body_b64" {
  description = "Base64 encoded content for the pull request body"
  type        = string
  sensitive   = true
}