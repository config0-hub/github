variable "url" {}
variable "insecure_ssl" { default = true }
variable "secret" { default = "secret123" }
variable "active" { default = true }
variable "content_type" { default = "json" }
variable "repository" { default = "config0-private-test" }
variable "events" { default = "push,pull_request" }
