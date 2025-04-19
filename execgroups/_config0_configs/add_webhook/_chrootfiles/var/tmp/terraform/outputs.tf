output "webhook_id" {
  description = "The ID of the created webhook"
  value       = github_repository_webhook.default.id
}

output "etag" {
  description = "The ETag of the webhook"
  value       = github_repository_webhook.default.etag
}

output "events" {
  description = "The list of events that trigger the webhook"
  value       = github_repository_webhook.default.events
}

output "url" {
  description = "The URL of the webhook"
  value       = github_repository_webhook.default.configuration[0].url
  sensitive   = true
}

output "repository" {
  description = "The repository where the webhook is installed"
  value       = github_repository_webhook.default.repository
}