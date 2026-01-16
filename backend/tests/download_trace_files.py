import argparse
import asyncio
import json
import os

import pyarrow.parquet as pq

from api.core.database import get_session
from api.core.s3 import S3Storage
from api.evaluations.repository import EvaluationRepository


async def run(user_id: str, trace_id: int) -> None:
    async for session in get_session():
        repository = EvaluationRepository(session)
        trace = await repository.get_trace_by_id(trace_id)
        if trace.user_id != user_id:
            raise ValueError("Trace does not belong to user")
        events = await repository.get_events_by_trace(trace_id)
        break

    base_dir = os.path.dirname(__file__)
    output_dir = os.path.join(base_dir, "trace_downloads", str(trace_id))
    os.makedirs(output_dir, exist_ok=True)

    events_path = os.path.join(output_dir, "trace_events.jsonl")
    with open(events_path, "w", encoding="utf-8") as file:
        for event in events:
            line = {
                "event_type": event.event_type,
                "trace_id": event.trace_id,
                "sample_id": event.sample_id,
                "guideline_name": event.guideline_name,
                "data": event.data,
                "created_at": event.created_at.isoformat() if event.created_at else None,
            }
            line = {key: value for key, value in line.items() if value is not None}
            file.write(json.dumps(line) + "\n")

    s3_path = next(
        event.data["s3_path"]
        for event in events
        if event.event_type == "sampling"
    )

    s3 = S3Storage()
    s3_output_dir = os.path.join(output_dir, "s3")
    os.makedirs(s3_output_dir, exist_ok=True)

    continuation = None
    while True:
        list_kwargs = {"Bucket": s3.bucket, "Prefix": s3_path}
        if continuation:
            list_kwargs["ContinuationToken"] = continuation
        response = s3.client.list_objects_v2(**list_kwargs)
        for obj in response.get("Contents", []):
            key = obj["Key"]
            if key.endswith("/"):
                continue
            if key.startswith(s3_path + "/"):
                relative_key = key[len(s3_path) + 1 :]
            else:
                relative_key = key
            local_path = os.path.join(s3_output_dir, relative_key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            s3.client.download_file(s3.bucket, key, local_path)
        if not response.get("IsTruncated"):
            break
        continuation = response.get("NextContinuationToken")

    for root, _, files in os.walk(s3_output_dir):
        for filename in files:
            if filename.endswith(".parquet"):
                parquet_path = os.path.join(root, filename)
                table = pq.read_table(parquet_path)
                rows = table.to_pylist()
                json_path = f"{parquet_path}.json"
                with open(json_path, "w", encoding="utf-8") as file:
                    json.dump(rows, file)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("user_id")
    parser.add_argument("trace_id", type=int)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(run(args.user_id, args.trace_id))
