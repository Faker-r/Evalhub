# Import existing EC2 instance

resource "aws_instance" "celery_worker" {
  ami           = "ami-0c55b159cbfafe1f0" # Placeholder - will be filled during import
  instance_type = "t3.medium"
  key_name      = "evalhub"
  subnet_id     = "subnet-027fa6ff0287a6478"

  vpc_security_group_ids = ["sg-052807540561ab35a"]

  tags = {
    Name = "evalhub-celery-worker"
  }

  lifecycle {
    ignore_changes = [ami]
  }
}
