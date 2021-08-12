resource "google_cloud_tasks_queue" "paginate" {
  name     = "${local.module_name}-paginate"
  location = local.region

  rate_limits {
    max_concurrent_dispatches = 1
  }
}

#---------------
# enqueuer
resource "google_project_iam_binding" "cloudtasks_enqueuer" {
  project = local.project_id
  role    = "roles/cloudtasks.enqueuer"

  members = flatten([
    # TODO: enum enqueuer
    formatlist(
      "serviceAccount:%s",
      [
        google_service_account.this.email,
      ]
    ),
  ])
}
