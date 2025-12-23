from flask import Blueprint, request, jsonify
from core.permissions import require_user
from core.pack_generator import generate_pack
from core.mailer import send_zip_email
from core.packs_repo import save_generated_pack, get_user_packs

client_bp = Blueprint("client", __name__, url_prefix="/client")


# ============================
# GENERAR PACK + EMAIL + DB
# ============================
@client_bp.post("/generate-pack")
@require_user
def generate_pack_route():
    payload = request.get_json() or {}

    pack_id = payload.get("pack_id")
    data = payload.get("data")

    if not pack_id or not isinstance(data, dict):
        return jsonify({"error": "Datos inválidos"}), 400

    # Usuario autenticado (inyectado por require_user)
    user_id = request.user["sub"]
    user_email = request.user["email"]

    # 1️⃣ Generar ZIP con documentos
    try:
        result = generate_pack(pack_id, data, user_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # 2️⃣ Enviar email (NO rompe si falla)
    email_result = send_zip_email(
        to_email="Inverplangu@gmail.com",
        zip_path=result["zip_path"]
    )

    # 3️⃣ Guardar en base de datos
    save_generated_pack(
        user_id=user_id,
        pack_id=pack_id,
        zip_name=result["zip_name"],
        zip_path=result["zip_path"],
        email_sent=email_result["sent"],
        email_error=email_result["error"]
    )

    # 4️⃣ Respuesta final
    return jsonify({
        "ok": True,
        "zip_download": f"/download/{result['zip_name']}",
        "email": email_result
    })


# ============================
# LISTAR PACKS DEL USUARIO
# ============================
@client_bp.get("/packs")
@require_user
def list_my_packs():
    user_id = request.user["sub"]
    packs = get_user_packs(user_id)

    return jsonify({
        "ok": True,
        "packs": packs
    })
