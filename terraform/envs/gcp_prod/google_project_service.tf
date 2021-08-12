resource "google_project_service" "services" {
  for_each = toset([
    "appengine.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudscheduler.googleapis.com",
    "cloudtasks.googleapis.com",
    "secretmanager.googleapis.com",
    "sheets.googleapis.com",
  ])

  project                    = local.project_id
  service                    = each.value
  disable_dependent_services = true
}

