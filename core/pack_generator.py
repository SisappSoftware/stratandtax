import os
import uuid
import json
import zipfile
import tempfile
import logging
from datetime import datetime
from core.generator import generate_document

# Logger
logger = logging.getLogger(__name__)

# Paths base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # /core
ROOT_DIR = os.path.dirname(BASE_DIR)                    # raíz proyecto
TMP_DIR = tempfile.gettempdir()                         # /tmp en Render


def generate_pack(pack_id: str, data: dict, user_id: int):
    logger.info("generate_pack START pack_id=%s user_id=%s", pack_id, user_id)
    logger.info("CWD=%s", os.getcwd())
    logger.info("ROOT_DIR=%s", ROOT_DIR)
    logger.info("TMP_DIR=%s", TMP_DIR)

    try:
        # --- Resolver pack_path ---
        pack_path = os.path.join(
            ROOT_DIR,
            "plantillas",
            "packs",
            pack_id
        )
        logger.info("Resolved pack_path=%s", pack_path)
        logger.info("pack_path exists=%s", os.path.isdir(pack_path))

        if not os.path.isdir(pack_path):
            logger.error("Pack path does not exist")
            raise ValueError("Pack inexistente")

        logger.info("Files in pack_path=%s", os.listdir(pack_path))

        # --- Leer pack.json ---
        pack_json_path = os.path.join(pack_path, "pack.json")
        logger.info(
            "Reading pack.json path=%s exists=%s",
            pack_json_path,
            os.path.exists(pack_json_path)
        )

        with open(pack_json_path, "r", encoding="utf-8") as f:
            pack_cfg = json.load(f)

        logger.info("pack_cfg loaded keys=%s", list(pack_cfg.keys()))
        logger.info("Declared docs=%s", pack_cfg.get("docs"))

        # --- Directorios temporales ---
        run_id = uuid.uuid4().hex
        run_dir = os.path.join(TMP_DIR, "stratandtax_docs", run_id)
        zip_dir = os.path.join(TMP_DIR, "stratandtax_zips")

        logger.info("Creating run_dir=%s", run_dir)
        logger.info("Creating zip_dir=%s", zip_dir)

        os.makedirs(run_dir, exist_ok=True)
        os.makedirs(zip_dir, exist_ok=True)

        generated_files = []

        # --- Generar DOCX ---
        for doc in pack_cfg["docs"]:
            template_path = os.path.join(pack_path, doc["template"])
            output_path = os.path.join(run_dir, doc["output"])

            logger.info(
                "Processing doc template=%s output=%s",
                doc["template"],
                doc["output"]
            )
            logger.info(
                "Template path=%s exists=%s",
                template_path,
                os.path.exists(template_path)
            )

            generate_document(
                template_path=template_path,
                output_path=output_path,
                data=data,
                user_id=user_id
            )

            logger.info(
                "Generated DOCX output_path=%s exists=%s",
                output_path,
                os.path.exists(output_path)
            )

            if not os.path.exists(output_path):
                logger.error("DOCX was not created: %s", output_path)
                raise RuntimeError("DOCX generation failed")

            generated_files.append(output_path)

        # --- Crear ZIP ---
        zip_name = f"{pack_id}_{run_id}.zip"
        zip_path = os.path.join(zip_dir, zip_name)

        logger.info("Creating ZIP at %s", zip_path)
        logger.info("Files to zip=%s", generated_files)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for f in generated_files:
                z.write(f, arcname=os.path.basename(f))

        logger.info(
            "ZIP created exists=%s size=%s",
            os.path.exists(zip_path),
            os.path.getsize(zip_path) if os.path.exists(zip_path) else None
        )

        if not os.path.exists(zip_path):
            logger.error("ZIP was not created")
            raise RuntimeError("ZIP generation failed")

        logger.info("generate_pack SUCCESS zip_name=%s", zip_name)

        return {
            "zip_path": zip_path,
            "zip_name": zip_name,
            "created_at": datetime.utcnow().isoformat()
        }

    except Exception:
        logger.exception("generate_pack FAILED")
        raise
