resource "google_cloudbuild_trigger" "terraform_proc" {
  name = var.name

  dynamic "github" {
    for_each = [var.github]
    content {
      owner = github.value["owner"]
      name  = github.value["name"]

      dynamic "pull_request" {
        for_each = github.value["pull_request"] != null ? [github.value["pull_request"]] : []
        content {
          branch          = lookup(pull_request.value, "branch", null)
          comment_control = lookup(pull_request.value, "comment_control", null)
          invert_regex    = lookup(pull_request.value, "invert_regex", null)
        }
      }

      dynamic "push" {
        for_each = github.value["push"] != null ? [github.value["push"]] : []
        content {
          branch       = lookup(push.value, "branch", null)
          tag          = lookup(push.value, "tag", null)
          invert_regex = lookup(push.value, "invert_regex", null)
        }
      }
    }
  }

  build {
    timeout = "${sum([for step in local.steps : step["timeout"]])}s"

    dynamic "step" {
      for_each = local.steps
      content {
        name       = local.terraform_docker_image
        id         = replace(step.value["id"], " ", "_")
        dir        = step.value["dir"]
        entrypoint = "terraform"
        args       = split(" ", step.value["args"])
        timeout    = "${step.value["timeout"]}s"
      }
    }
  }
}

