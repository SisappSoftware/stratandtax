import os
import uuid
import json
import zipfile
from datetime import datetime
from core.generator import generate_document



PACKS_DIR = "plantillas/packs"
OUTPUT_DOCS = "outputs/docs"
OUTPUT_ZIPS = "outputs/zips"


def generate_pack(pack_id: str, data: dict, user_id: int):
    print("=== DEBUG PACK GENERATOR ===")
    print("CWD:", os.getcwd())
    print("PACK_ID:", pack_id)

    pack_path = os.path.join(PACKS_DIR, pack_id)
    print("PACK_PATH:", pack_path)

    if not os.path.isdir(pack_path):
        print("ERROR: pack_path no existe")
        raise ValueError("Pack inexistente")

    print("FILES EN PACK_PATH:", os.listdir(pack_path))

    pack_path = os.path.join(PACKS_DIR, pack_id)
    if not os.path.isdir(pack_path):
        raise ValueError("Pack inexistente")

    with open(os.path.join(pack_path, "pack.json"), "r", encoding="utf-8") as f:
        pack_cfg = json.load(f)

    run_id = uuid.uuid4().hex
    run_dir = os.path.join(OUTPUT_DOCS, run_id)
    os.makedirs(run_dir, exist_ok=True)
    os.makedirs(OUTPUT_ZIPS, exist_ok=True)

    generated_files = []

    for doc in pack_cfg["docs"]:
        template_path = os.path.join(pack_path, doc["template"])
        print("INTENTANDO ABRIR TEMPLATE:", template_path)
        print("EXISTE?:", os.path.exists(template_path))
        output_path = os.path.join(run_dir, doc["output"])

        generate_document(
            template_path,
            output_path,
            data,
            user_id
        )

        generated_files.append(output_path)

    zip_path = os.path.join(OUTPUT_ZIPS, f"{pack_id}_{run_id}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in generated_files:
            z.write(f, arcname=os.path.basename(f))

    return {
        "zip_path": zip_path,
        "zip_name": os.path.basename(zip_path),
        "created_at": datetime.utcnow().isoformat()
    }
