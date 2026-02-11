variable "url" {
  description = "The URL to which the payloads will be delivered"
  type        = string
}

variable "insecure_ssl" {
  description = "Whether to allow insecure SSL connections to the webhook URL"
  type        = bool
  default     = true
}

variable "secret" {
  description = "Secret key used to sign the webhook payload"
  type        = string
  default     = "secret123"
  sensitive   = true
}

variable "active" {
  description = "Whether the webhook is active"
  type        = bool
  default     = true
}

variable "content_type" {
  description = "The content type for the payload (json or form)"
  type        = string
  default     = "json"
  validation {
    condition     = contains(["json", "form"], var.content_type)
    error_message = "The content_type must be either 'json' or 'form'."
  }
}

variable "repository" {
  description = "The name of the GitHub repository to add the webhook to"
  type        = string
  default     = "config0-private-test"
}

variable "events" {
  description = "Comma-separated list of GitHub events to trigger the webhook"
  type        = string
  default     = "push,pull_request"
}

