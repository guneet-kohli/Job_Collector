from collector import LinkedInCollector

collector = LinkedInCollector()

collector.login()

collector.collect_jobs()

collector.save()