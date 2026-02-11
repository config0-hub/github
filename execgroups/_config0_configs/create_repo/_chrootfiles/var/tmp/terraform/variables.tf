# Input Variables
variable "repository" {
  description = "Name of the GitHub repository to create"
  type        = string
  default     = "private-test"
}

variable "visibility" {
  description = "Visibility of the repository (private, public, or internal)"
  type        = string
  default     = "private"
  validation {
    condition     = contains(["private", "public", "internal"], var.visibility)
    error_message = "Valid values for visibility are: private, public, or internal."
  }
}

variable "has_issues" {
  description = "Enable GitHub issues for this repository"
  type        = bool
  default     = true
}

variable "has_projects" {
  description = "Enable GitHub projects for this repository"
  type        = bool
  default     = false
}

variable "has_wiki" {
  description = "Enable GitHub wiki for this repository"
  type        = bool
  default     = false
}

variable "delete_branch_on_merge" {
  description = "Automatically delete head branch after a pull request is merged"
  type        = bool
  default     = true
}

variable "default_branch" {
  description = "Name of the default branch for this repository"
  type        = string
  default     = "main"
}