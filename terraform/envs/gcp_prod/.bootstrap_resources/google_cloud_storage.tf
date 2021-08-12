resource "google_storage_bucket" "terraform" {
  name     = "${var.project_name}-terraform"
  location = upper(local.region)

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      days_since_noncurrent_time = 32
    }
    action {
      type = "Delete"
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}

