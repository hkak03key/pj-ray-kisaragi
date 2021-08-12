#=====================
# twitter_api

resource "google_secret_manager_secret" "twitter_api" {
  secret_id = "${local.module_name}-twitter-api"
  replication {
    automatic = true
  }
}

#---------------
# secretAccessor
resource "google_secret_manager_secret_iam_binding" "twitter" {
  secret_id = google_secret_manager_secret.twitter_api.secret_id
  role      = "roles/secretmanager.secretAccessor"
  members = flatten([
    # TODO: enum secretAccessor
    formatlist(
      "serviceAccount:%s",
      [
        google_service_account.this.email,
      ]
    ),
  ])

  depends_on = [
    google_secret_manager_secret.twitter_api,
  ]
}
