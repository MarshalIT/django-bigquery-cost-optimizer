import json
import tempfile
from django.core.management.base import BaseCommand
from django.utils import timezone
from google.cloud import bigquery
from myapp.models import UserEvent


class Command(BaseCommand):
    help = "Batch-loads incremental Django UserEvent records into BigQuery."

    def handle(self, *args, **options):
        client = bigquery.Client()
        table_id = "your-gcp-project.analytics.user_events_optimized"

        # Fetch un-synced records in batches to keep memory flat
        queryset = UserEvent.objects.filter(synced_to_bq=False).iterator(chunk_size=5000)

        rows = []
        event_ids = []
        for event in queryset:
            rows.append({
                "event_id": str(event.id),
                "customer_id": event.customer_id,
                "event_type": event.event_type,
                "revenue_usd": str(event.revenue_usd),
                "event_timestamp": event.created_at.isoformat(),
            })
            event_ids.append(event.id)

        if not rows:
            self.stdout.write("No new events to sync.")
            return

        # Write newline-delimited JSON to use free BigQuery batch loading
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".jsonl") as tmp_file:
            for row in rows:
                tmp_file.write(json.dumps(row) + "\n")
            tmp_file.flush()
            tmp_file.seek(0)

            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            )
            load_job = client.load_table_from_file(tmp_file, table_id, job_config=job_config)
            load_job.result()  # Wait for completion

        UserEvent.objects.filter(id__in=event_ids).update(
            synced_to_bq=True, synced_at=timezone.now()
        )
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(rows)} events to BigQuery."))
