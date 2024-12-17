provider "github" {}

resource "github_repository_webhook" "default" {

  repository = var.repository

  configuration {
    url          = var.url
    insecure_ssl = var.insecure_ssl
    content_type = var.content_type
    secret       = var.secret
  }

  active = var.active
  events = split(",",var.events)

}
