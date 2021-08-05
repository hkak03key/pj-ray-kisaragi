
resource "google_secret_manager_secret" "twitter_api" {
  secret_id = "twitter_api"
  replication {
    automatic = true
  }
}
