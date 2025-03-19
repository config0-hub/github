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
  events = split(",", var.events)

}

output "webhook_id" {
  value = github_repository_webhook.default.id
}

output "etag" {
  value = github_repository_webhook.default.etag
}

output "events" {
  value = github_repository_webhook.default.events
}

output "url" {
  value     = github_repository_webhook.default.configuration[0].url
  sensitive = true
}

output "repository" {
  value = github_repository_webhook.default.repository
}
