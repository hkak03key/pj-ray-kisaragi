resource "google_app_engine_application" "app" {
  project     = local.project_name
  location_id = local.project_region

  depends_on = [
    google_project_service.services,
  ]
}
