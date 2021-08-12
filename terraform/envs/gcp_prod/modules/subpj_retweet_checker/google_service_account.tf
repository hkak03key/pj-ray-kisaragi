resource "google_service_account" "this" {
  account_id   = local.module_name
  display_name = ""
}


#---------------
# iam_service_account_user
resource "google_project_iam_binding" "iam_service_account_user" {
  project = local.project_id
  role    = "roles/iam.serviceAccountUser"

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
