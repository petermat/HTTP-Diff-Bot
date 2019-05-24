# HTTP-Diff-Bot

HTTP-Diff-Bot is Django powered application to compare and alert on changes of HTTP and HTML responses.
Insert URL or Domain and receive email every time a change is observed.

Features:
	- Alert on change of HTTP status code (200 -> 404)
	- Alert on change of HTML content within defined thresholds
	- Show side-by-side comparison of HTML changes between last snapshots
	- Show dashboard with taken snapshots and raised alerts


### Prerequisites

- OS: Linux (referred), OS X or Windows
- Python >= 3.6
- Apache/Nginx  (Production Deployment only)

### Installing

- VENV

- pip install -r requirements

## Production Deployment

- Always generate new SECRET_KEY!
	Run command: `python manage.py shell -c 'from django.core.management import utils; print(utils.get_random_secret_key())'` and replace SECRET_KEY value in `project/settings.py`.

- Reverse proxy for production environment

- CRON

## Getting Started

Rename file `project/local.RENAME.py` to `local.py` and edit `ALLOWED_HOSTS` and SMTP settings

Initial database structure
	`python manage.py makemigrations checkweb`
	`python manage.py migrate`

To fill project with test data run following:
	`python manage.py hopper`

Application is now ready to run

## Running the tests

Tests not implemented yet.


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
