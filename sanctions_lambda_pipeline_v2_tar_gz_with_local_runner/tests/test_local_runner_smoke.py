import json
import csv
import tarfile
from pathlib import Path
from pipeline import run_pipeline_from_files


def _make_tar_gz_with_member(tmp_path: Path, member_name: str, member_bytes: bytes) -> str:
    tar_path = tmp_path / "output.tar.gz"
    member_file = tmp_path / "member"
    member_file.write_bytes(member_bytes)
    with tarfile.open(tar_path, "w:gz") as tf:
        tf.add(member_file, arcname=member_name)
    return str(tar_path)


def test_local_pipeline_from_files(tmp_path):
    sanctions_csv = tmp_path / "sanctions.csv"
    with sanctions_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["sanction_list"])
        w.writeheader()
        w.writerow({"sanction_list": "Jon Julu;Exxon, Inc"})

    mapping = [
        {"Line": 1, "content": "I met Jon Julu yesterday.", "sentence_id": "s1"},
        {"Line": 2, "content": "EXXON INC reported earnings.", "sentence_id": "s2"},
    ]
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(json.dumps(mapping), encoding="utf-8")

    comp_lines = [
        {"Entities": [{"Text": "Jon Julu", "BeginOffset": 6, "EndOffset": 13, "Type": "PERSON", "Score": 0.99}]},
        {"Entities": [{"Text": "EXXON INC", "BeginOffset": 0, "EndOffset": 9, "Type": "ORGANIZATION", "Score": 0.98}]},
    ]
    jsonl_bytes = ("\n".join(json.dumps(x) for x in comp_lines) + "\n").encode("utf-8")
    tar_path = _make_tar_gz_with_member(tmp_path, "part-00000", jsonl_bytes)

    payload = run_pipeline_from_files(
        sanctions_csv_path=str(sanctions_csv),
        mapping_json_path=str(mapping_path),
        comprehend_tar_gz_path=tar_path,
    )

    assert payload["meta"]["uniqueSentences"] == 2
    assert payload["meta"]["sanctionedEntities"] >= 2
