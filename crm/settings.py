"""
CRM App Settings
Django-crontab configuration for scheduled jobs
"""

# Django Crontab
INSTALLED_APPS = ['django_crontab']

# Cron Jobs Configuration
CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
]
