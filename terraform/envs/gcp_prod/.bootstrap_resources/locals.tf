locals {
  project_id = data.google_project.project.number
  region     = data.google_client_config.this.region
}

