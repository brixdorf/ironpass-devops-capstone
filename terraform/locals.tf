locals {
  tags = {
    Project     = var.project
    ManagedBy   = "terraform"
    Environment = var.environment
  }
}
