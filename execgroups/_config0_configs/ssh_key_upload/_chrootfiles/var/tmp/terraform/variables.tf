# Input variables
variable "key_name" {
  description = "The title of the deploy key to be created"
  type        = string
  validation {
    condition     = length(var.key_name) > 0
    error_message = "The key_name value must not be empty."
  }
}

variable "public_key_hash" {
  description = "The base64 encoded public key hash to use as the deploy key"
  type        = string
  sensitive   = true
  validation {
    condition     = length(var.public_key_hash) > 0
    error_message = "The public_key_hash value must not be empty."
  }
}

variable "read_only" {
  description = "Determines if the deploy key has read-only access or read-write access"
  type        = bool
  default     = true
}

variable "repository" {
  description = "The GitHub repository where the deploy key will be added"
  type        = string
  default     = "config0-private-test"
}

