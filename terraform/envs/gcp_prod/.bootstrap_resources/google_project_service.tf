resource "google_project_service" "services" {
  for_each = toset([
    "cloudbuild.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
  ])

  project                    = local.project_id
  service                    = each.value
  disable_dependent_services = true
}

