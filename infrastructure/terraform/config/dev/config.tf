terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket       = "the-yield-terraform-state-bucket"
    key          = "dev.tfstate"
    region       = "eu-central-1"
    encrypt      = true
    use_lockfile = true
  }
}

# --- Configure the AWS Provider ---
provider "aws" {
  region = "eu-central-1"

  default_tags {
    tags = {
      Creator = "Terraform"
      Stage   = "dev"
      Project = "the-yield"
    }
  }
}

# ====================================
# --- MAIN ---
# ====================================

module "api" {
  source = "../../services"

  stage        = "dev"
  project_name = "the-yield"

  # --- Cognito ---
  cognito = {
    enabled             = true
    password_min_length = 8
    callback_urls       = ["https://checkmeineimmo.de/auth/callback"]
    logout_urls         = ["https://checkmeineimmo.de/auth/logout"]
  }
}
