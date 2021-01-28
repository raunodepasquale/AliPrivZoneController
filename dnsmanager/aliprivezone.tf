variable accessKey {}
variable secretKey {}
variable region {}
variable privZoneId {}
variable hostName {}
variable targetIp {}

provider "alicloud" {
  access_key = var.accessKey
  secret_key = var.secretKey
  region     = var.region
}
resource "alicloud_pvtz_zone_record" "record" {
  zone_id         = var.privZoneId
  rr              = var.hostName
  type            = "A"
  value           = var.targetIp
  ttl             = 60
}
